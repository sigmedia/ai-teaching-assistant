import json
import aiohttp
from config import settings
from utils.logger import logger
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from markdown_it import MarkdownIt
import re
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import init_db, get_db, async_session_maker
from utils.session import create_session, get_session, expire_session, save_message, format_message_history, expire_sessions
from utils.scheduler import SchedulerManager
from utils.validation import InputValidator
from datetime import datetime
import time
import traceback

# Version information
__version__ = "1.0.1-dev"

# Set variables
AC_TIMEOUT = aiohttp.ClientTimeout(
    total=45,
    connect=5,
    sock_read=35,
    sock_connect=5
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_time = time.time()
    logger.info("=== Application Startup Begin ===")

    try:
        # Create client session
        client_session_start = time.time()
        app.state.client_session = aiohttp.ClientSession(timeout=AC_TIMEOUT)
        logger.info(f"Client session created in {time.time() - client_session_start:.2f} seconds")

        # Database initialization
        db_init_start = time.time()
        try:
            await init_db()
            logger.info(f"Database initialized in {time.time() - db_init_start:.2f} seconds")
        except Exception as db_init_error:
            logger.error(f"Database initialization failed: {db_init_error}")
            raise

        # Scheduler initialization
        scheduler_init_start = time.time()
        scheduler = SchedulerManager.get_scheduler()
        app.state.scheduler = scheduler
        logger.info(f"Scheduler retrieved in {time.time() - scheduler_init_start:.2f} seconds")

        # Scheduler job setup
        if SchedulerManager.should_start_scheduler() and not scheduler.running:
            scheduler_job_start = time.time()
            async def run_expire_sessions():
                logger.info("Starting session expiry job")
                try:
                    async with async_session_maker() as db:
                        await expire_sessions(db)
                        logger.info("Session expiry completed successfully")
                except Exception as e:
                    logger.error(f"Error in session cleanup job: {str(e)}")
                    logger.error(traceback.format_exc())
            
            try:
                freq_mins = int(settings.SCHEDULER_FREQ_MINS)
                scheduler.add_job(
                    id="session_cleanup",
                    func=run_expire_sessions,
                    trigger="interval",
                    minutes=freq_mins,
                    max_instances=1,
                    next_run_time=datetime.now()
                )
                scheduler.start()
                logger.info(f"Scheduler started in {time.time() - scheduler_job_start:.2f} seconds")
            except Exception as e:
                logger.error(f"Scheduler setup failed: {str(e)}")

        total_startup_time = time.time() - start_time
        logger.info(f"=== Application Startup Complete in {total_startup_time:.2f} seconds ===") 
        yield
        
    except Exception as e:
        logger.error(f"Critical startup error: {str(e)}")
        raise
    
    finally:
        shutdown_start = time.time()
        logger.info("=== Starting Application Shutdown ===")
        
        try:
            await app.state.client_session.close()
            logger.info("Client session closed")
        except Exception as e:
            logger.error(f"Error closing client session: {str(e)}")
        
        try:
            scheduler = getattr(app.state, 'scheduler', None)
            if scheduler and scheduler.running:
                scheduler.shutdown()
                logger.info("Scheduler shutdown complete")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {str(e)}")
        
        SchedulerManager.cleanup()
        
        total_shutdown_time = time.time() - shutdown_start
        logger.info(f"=== Application Shutdown Complete in {total_shutdown_time:.2f} seconds ===")

# Create FastAPI app FIRST
startup_time = time.time()
logger.info("Initializing FastAPI application")
app = FastAPI(lifespan=lifespan)
logger.info(f"FastAPI app created in {time.time() - startup_time:.2f} seconds")

# Markdown initialization logging
md_init_start = time.time()
md = MarkdownIt("zero", {
    'html': True,
    'xhtmlOut': True,
    'breaks': False,
    'typographer': False
})

# Enable only the features needed
md.enable([
    'heading',
    'paragraph',
    'list',
    'table',
    'code',
    'fence',
    'strikethrough',
    'backticks',
    'link'
])
logger.info(f"Markdown parser initialized in {time.time() - md_init_start:.2f} seconds")

async def convert_markdown(text):
    html=md.render(text)
    html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html)
    html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', html)
    return html

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", 
        {
            "request": request, 
            "bot_name": settings.BOT_NAME, 
            "course_name": settings.COURSE_NAME
        }
    )

@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request, db: AsyncSession = Depends(get_db)):

    return templates.TemplateResponse(
        "privacy.html",
        {
            "request": request, 
            "bot_name": settings.BOT_NAME, 
            "course_name": settings.COURSE_NAME
        }
    )

@app.post("/login")
async def login(request: Request, validation_response: dict = Depends(InputValidator.validate_login_data), db: AsyncSession = Depends(get_db)):
    
    error_message = ""
    if not validation_response["check_code"]:
        print(validation_response)
        error_message = validation_response["message"]
    else:
        login_data = validation_response["login_data"]
        session_id = await create_session(login_data["agreement_part_1"], login_data["agreement_part_2"], db)
        if session_id:
            # Redirect to main page
            request.session["anon_session"] = session_id
            logger.info(f"Session {session_id} stored in request", event_type="aita") 
            return RedirectResponse(url="/", status_code=303)
        else:
            error_message = "There was an issue logging you in. If you still want to proceed, please try again later."
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "bot_name": settings.BOT_NAME,
            "course_name": settings.COURSE_NAME,
            "error": error_message
        }
    )

@app.get("/")
async def home(request: Request, db: AsyncSession = Depends(get_db)):

    session = await get_session(request.session, db)
    if not session:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("chat.html", {"request": request, "bot_name": settings.BOT_NAME, "course_name": settings.COURSE_NAME})

@app.post("/send")
async def send_message(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    session = await get_session(request.session, db)
    if not session:
        return RedirectResponse(url="/login", status_code=303)
    session_id = session.SessionID
    
    form_data = await request.form()
    user_message = form_data.get("user_message")
    
    try:
        await InputValidator.validate_chat_message(user_message)
    except HTTPException as e:
        error_text = f"Chat input failed validation in session {session_id}. Error message: {str(e)}"
        logger.error(error_text, event_type="aita") 
        if e.status_code == 403:
            return RedirectResponse(url="/login", status_code=303)
    except Exception as e:
        error_text = f"Chat input unknown exception in session {session_id}. Error message: {str(e)}"
        logger.error(error_text, event_type="aita")

    # Get chat history before saving user message
    chat_history = await format_message_history(session_id, db)

    # Save user message
    await save_message(session_id, False, user_message, db)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.CHAT_API_KEY}"
    }

    data = {"chat_input": user_message, "chat_history": chat_history}
    bot_message = ""

    try:
        async with app.state.client_session.post(
            settings.CHAT_API_ENDPOINT, json=data, headers=headers
        ) as response:

            # Get bot response
            result_bytes = await response.read()
            result_text = result_bytes.decode('utf-8')
            result = json.loads(result_text)  # Parse JSON

            # Get bot message
            bot_message = result["chat_output"]

            # Save bot message before processing markdown to HTML
            await save_message(session_id, True, bot_message, db)
            bot_message_html = await convert_markdown(bot_message)

    except Exception as e:

        if 'content_filter' in result['error']['message']:
            error_text = f"Chat request failed. Content filter error."
            logger.error(error_text, event_type="aita")
            bot_message = "Apologies, but something in the content of your message seems unsafe to me. Can you clarify or provide additional details?"
        else:
            error_text = f"Chat request failed. Error type {type(e).__name__}. Error message: {str(e)}"
            logger.error(error_text, event_type="aita")
            bot_message = "Apologies, but I'm not available right now. Please try again later."
    
        # Save bot message
        await save_message(session_id, True, bot_message, db)
        bot_message_html = "<p>"+bot_message+"</p>"

    return JSONResponse(
        {
            "status": "success",
            "message": bot_message_html
        }
    )

@app.get("/logout")
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):

    await expire_session(request.session, db)
    logger.info(f"Logging user out.", event_type="aita")
    response.delete_cookie("session")
    return RedirectResponse(url="/login", status_code=302)

# Template and static files initialization logging
templates_init_start = time.time()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
logger.info(f"Templates and static files mounted in {time.time() - templates_init_start:.2f} seconds")

# Middleware initialization logging
middleware_init_start = time.time()
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.MIDDLEWARE_SECRET,
    session_cookie="anon_session",
    max_age=None,  # Browser session only
    same_site="Strict",
    https_only=(settings.ENVIRONMENT=='prod')
)
logger.info(f"Middleware added in {time.time() - middleware_init_start:.2f} seconds")



