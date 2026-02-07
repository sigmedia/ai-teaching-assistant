# Data Analysis Notes

## Usage Data (Messages Activity)

- To calculate the number of active sessions during exam hour (15:00-15:59 on March 19, 2025), we counted sessions either a) newly created, or b) already active, and having at least one query, during that period.
- To calculate the number of queries during exam hour (15:00-15:59 on March 19, 2025), we counted only queries that actually occurred during that period.
- Note: The app automatically closes open sessions after a defined period of inactivity, via regularly scheduled job. The period of inactivity and job frequency are set using environment variables. For the MPE 2025 deployment, MAX_INACTIVE_TIME_MINS was set to 720 and SCHEDULER_FREQ_MINS was set to 180.

## Performance Data (Student Exam Scores)

- PerformanceData_StudentExamScores.txt and PerformanceData_StudentExamScores.csv contain one row per student, with a column per exam score (Test1, Test2, Test3).
- PerformanceData_StudentExamScores.csv has an additional column with the mean exam score per student.
- After acquiring [bootstrap.py](https://www.sjeng.org/ftp/bootstrap.py), run the following commands:

```
deactivate
pyenv shell 2.7.18
python bootstrap.py --compare-all --blocked PerformanceData_StudentExamScores.txt
