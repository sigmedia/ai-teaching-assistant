import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
import textwrap


def create_topic_visualization(input_path, output_path, title_prefix=""):
    """Build an interactive HTML page from a clustered, t-SNE-reduced dataset.

    The page stacks two linked Plotly figures: a bar chart of query counts per
    topic (top) and a 3D t-SNE scatter of every query coloured by topic
    (bottom). Clicking a bar shows/hides the matching cluster in the scatter.

    Args:
        input_path: CSV with one row per query. Expected columns: 'cluster',
            'tsne_1'/'tsne_2'/'tsne_3', 'MessageText', and optionally
            'topic_label', 'DateCreated_Message', 'SessionID', 'Id'.
        output_path: Where to write the HTML. A 'plotly.min.js' file is written
            alongside it so the page renders without internet access.
        title_prefix: Text prepended to the page heading (e.g. a course/year).

    Returns:
        The DataFrame of plotted points, with the derived columns added.
    """

    print("Preparing 3D visualization of labeled topics")

    clustered_data = pd.read_csv(input_path)

    # Unique cluster IDs and how many queries fall in each
    clusters = sorted(clustered_data['cluster'].unique())
    cluster_sizes = clustered_data['cluster'].value_counts().to_dict()

    # Build a display label for every cluster. topic_labels holds a guaranteed
    # unique label (with the size appended) used as the scatter's colour key;
    # raw_topic_labels holds the plain human label used in tooltips and bar ticks.
    topic_labels = {}
    raw_topic_labels = {}
    used_labels = set()

    for cluster in clusters:
        if 'topic_label' in clustered_data.columns:
            topic_label = clustered_data[clustered_data['cluster'] == cluster]['topic_label'].iloc[0]

            # Fall back to the cluster ID when no label was assigned
            if pd.isna(topic_label) or topic_label == '' or topic_label is None:
                topic_label = f"Cluster {cluster}"
        else:
            topic_label = f"Cluster {cluster}"

        raw_topic_labels[cluster] = topic_label

        topic_size = cluster_sizes.get(cluster, 0)

        # Two clusters can share a topic label; disambiguate so each cluster
        # maps to a distinct key (Plotly needs unique category names).
        base_label = f"{topic_label} (size: {topic_size})"
        unique_label = base_label

        if unique_label in used_labels:
            unique_label = f"{topic_label} [Cluster {cluster}] (size: {topic_size})"

        counter = 1
        while unique_label in used_labels:
            unique_label = f"{topic_label} [Cluster {cluster}-{counter}] (size: {topic_size})"
            counter += 1

        topic_labels[cluster] = unique_label
        used_labels.add(unique_label)

    print(f"Created {len(topic_labels)} unique topic labels")

    # Largest clusters first; this order drives both the scatter trace order
    # and the left-to-right order of the bars, keeping the two in sync.
    clusters_by_size = sorted(clusters, key=lambda x: cluster_sizes.get(x, 0), reverse=True)

    if 'tsne_1' in clustered_data.columns and 'tsne_2' in clustered_data.columns and 'tsne_3' in clustered_data.columns:
        clustered_data['has_viz'] = clustered_data['tsne_1'].notna()
        print(f"Found t-SNE coordinates for {clustered_data['has_viz'].sum()} points")

    # Only rows with t-SNE coordinates can be plotted
    viz_data = clustered_data[clustered_data['has_viz']].copy()
    if len(viz_data) == 0:
        print("Error: No points have visualisation coordinates. Cannot create visualisation")
        return clustered_data

    print(f"Visualising {len(viz_data)} points across {len(clusters)} topics")

    # Axis ranges are fixed (rather than auto-scaled) so the cube stays put when
    # clusters are toggled. A small margin keeps points off the axis walls.
    x_min, x_max = viz_data['tsne_1'].min(), viz_data['tsne_1'].max()
    y_min, y_max = viz_data['tsne_2'].min(), viz_data['tsne_2'].max()
    z_min, z_max = viz_data['tsne_3'].min(), viz_data['tsne_3'].max()

    x_range = x_max - x_min
    y_range = y_max - y_min
    z_range = z_max - z_min
    x_min -= 0.025 * x_range
    x_max += 0.025 * x_range
    y_min -= 0.025 * y_range
    y_max += 0.025 * y_range
    z_min -= 0.025 * z_range
    z_max += 0.025 * z_range

    try:
        print("Creating interactive 3D visualization")

        # topic_name is the per-point colour key (one scatter trace per cluster);
        # topic_clean is the plain label shown in tooltips.
        viz_data['topic_name'] = viz_data['cluster'].apply(
            lambda x: topic_labels.get(x, f'Cluster {x}')
        )
        viz_data['topic_clean'] = viz_data['cluster'].apply(
            lambda x: raw_topic_labels.get(x, f'Cluster {x}')
        )

        # Category order = clusters largest-first, so scatter trace index i
        # corresponds to bar i in the bar chart.
        ordered_categories = [topic_labels.get(c, f'Cluster {c}') for c in clusters_by_size]

        # topic_labels should already be unique; this is a last-resort guard so
        # a duplicate can never collapse two clusters into one category.
        if len(ordered_categories) != len(set(ordered_categories)):
            print("Warning: Found duplicate categories.")
            print("Duplicate categories:", [cat for cat in ordered_categories if ordered_categories.count(cat) > 1])
            seen = set()
            unique_ordered = []
            for cat in ordered_categories:
                if cat not in seen:
                    unique_ordered.append(cat)
                    seen.add(cat)
                else:
                    unique_ordered.append(f"{cat}_DUPLICATE")
            ordered_categories = unique_ordered
            print("Fixed by adding _DUPLICATE suffix")

        # Make topic_name an ordered categorical so Plotly emits traces in
        # clusters_by_size order.
        viz_data['topic_name'] = pd.Categorical(
            viz_data['topic_name'],
            categories=ordered_categories,
            ordered=True
        )

        # Tooltip preview of the query text: truncate long messages, then wrap
        # to keep the hover box from stretching across the screen.
        def make_preview(text):
            text = text[:150] + "..." if len(text) > 150 else text
            return '<br>'.join(textwrap.wrap(str(text), 75)) or str(text)

        viz_data['message_preview_hover'] = viz_data['MessageText'].apply(make_preview)

        # Show timestamps in Dublin local time; fall back to the raw value if
        # the column is missing or can't be parsed.
        if 'DateCreated_Message' in viz_data.columns:
            try:
                dublin_tz = pytz.timezone('Europe/Dublin')
                viz_data['formatted_date'] = pd.to_datetime(viz_data['DateCreated_Message'], utc=True) \
                    .dt.tz_convert(dublin_tz) \
                    .dt.strftime('%Y-%m-%d %H:%M:%S (Dublin)')
            except Exception as e:
                print(f"Warning: Could not convert dates to Dublin time: {str(e)}")
                print("Using original date format instead")
                viz_data['formatted_date'] = viz_data['DateCreated_Message']
        else:
            print("Warning: DateCreated_Message column not found in dataset")
            viz_data['formatted_date'] = "Date not available"

        # Fields passed to the hover tooltip. The order here sets the
        # customdata[N] index each field gets in the hovertemplate below.
        hover_data = {
            'topic_clean': True,            # customdata[0]
            'message_preview_hover': True,  # customdata[1]
            'formatted_date': True,         # customdata[2]
            'SessionID': True,              # customdata[3]
            'Id': True,                     # customdata[4]
            'tsne_1': False,  # coordinates are the axes, not tooltip content
            'tsne_2': False,
            'tsne_3': False
        }

        fig = px.scatter_3d(
            viz_data,
            x='tsne_1',
            y='tsne_2',
            z='tsne_3',
            color='topic_name',
            hover_data=hover_data,
            opacity=0.7,
            title=f'<b>3D Visualization of Student Queries in {len(clusters)} Topic Clusters</b>',
            color_discrete_sequence=px.colors.qualitative.Bold,
            category_orders={'topic_name': ordered_categories}  # keep traces aligned with the bars
        )

        # Plotly's own legend is turned off; the bar chart above the plot serves
        # as a clickable legend instead. Axis ranges are locked to the values
        # computed above so toggling clusters doesn't rescale the cube.
        fig.update_layout(
            title=dict(
                text=(f'<b>3D Visualization of Student Queries '
                      f'in {len(clusters)} Topic Clusters</b>'),
                x=0.5, xanchor='center', y=0.93, yanchor='top',
                font=dict(size=22, color='#222')
            ),
            showlegend=False,
            autosize=True,
            paper_bgcolor='white',
            scene=dict(
                xaxis=dict(title=dict(text='t-SNE Dimension 1', font=dict(size=24)),
                           tickfont=dict(size=11),
                           range=[x_min, x_max], showspikes=False),
                yaxis=dict(title=dict(text='t-SNE Dimension 2', font=dict(size=24)),
                           tickfont=dict(size=11),
                           range=[y_min, y_max], showspikes=False),
                zaxis=dict(title=dict(text='t-SNE Dimension 3', font=dict(size=24)),
                           tickfont=dict(size=11),
                           range=[z_min, z_max], showspikes=False),
                aspectmode='cube'  # equal-length axes so the scene fills its canvas
            ),
            margin=dict(l=5, r=5, b=5, t=60)
        )

        # Marker style and the tooltip layout (indices map to hover_data above)
        fig.update_traces(
            marker=dict(
                size=6,
                line=dict(width=0)  # no outline around points
            ),
            hovertemplate =
                '<b>Student Query:</b> %{customdata[1]}<br>' +
                '<b>Topic:</b> %{customdata[0]}<br>' +
                '<b>Date:</b> %{customdata[2]}<br>' +
                '<b>Session ID:</b> %{customdata[3]}<br>' +
                '<b>Query ID:</b> %{customdata[4]}<extra></extra>'
        )

        # Give each tooltip a border in its own cluster's colour. Set per trace
        # because the colour differs from one trace to the next.
        for trace in fig.data:
            trace.update(
                hoverlabel=dict(
                    bgcolor="white",
                    font=dict(color="black", size=22),
                    bordercolor=trace.marker.color
                )
            )

        # Look up each cluster's scatter colour so the bars can be drawn in the
        # same colours as their points.
        name_to_color = {tr.name: tr.marker.color for tr in fig.data}

        # Bar chart data, largest cluster first. Bars use numeric x positions so
        # clusters that share a topic label remain distinct bars; the plain
        # topic label is shown as the tick text.
        bar_pos = list(range(len(clusters_by_size)))
        bar_ticktext = [raw_topic_labels.get(c, f'Cluster {c}') for c in clusters_by_size]
        bar_counts = [cluster_sizes.get(c, 0) for c in clusters_by_size]
        bar_colors = [name_to_color.get(topic_labels.get(c), '#888888') for c in clusters_by_size]

        bar_fig = go.Figure(
            go.Bar(
                x=bar_pos,
                y=bar_counts,
                width=0.6,
                marker=dict(color=bar_colors, opacity=[1.0] * len(bar_pos)),
                showlegend=False,
                customdata=bar_ticktext,
                hovertemplate='<b>%{customdata}</b><br>Queries: %{y}<br>'
                              '<i>Click to show/hide in 3D visualization below</i><extra></extra>',
                text=bar_counts,
                textposition='outside',
                textfont=dict(size=14),
                cliponaxis=False  # let the count labels sit above the tallest bar
            )
        )
        bar_fig.update_layout(
            showlegend=False,
            autosize=True,
            title=dict(
                text='<b>Student Queries per Topic</b>',
                x=0.5, xanchor='center', y=0.98, yanchor='top',
                font=dict(size=22, color='#222')
            ),
            # Generous fixed margins leave room for the steeply rotated tick
            # labels so a browser resize can't reflow and clip them.
            margin=dict(l=190, r=120, b=240, t=60),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        bar_fig.update_xaxes(
            tickmode='array',
            tickvals=bar_pos,
            ticktext=bar_ticktext,
            tickangle=-60,
            tickfont=dict(size=14),
            ticks='',          # no tick marks
            showgrid=False,
            zeroline=False,
            automargin=True,
            autorange=False,
            # Pin the range (with edge padding) so a width resize can't reflow
            # and clip the first or last bar and its label.
            range=[-0.7, len(bar_pos) - 0.3]
        )
        bar_fig.update_yaxes(
            title_text='',         # the count is printed on each bar instead
            ticks='',
            showticklabels=False,  # no numeric scale; counts are on the bars
            showgrid=False,
            zeroline=False,
            range=[0, max(bar_counts) * 1.15]  # a little headroom above the tallest bar
        )

        # Render each figure as a standalone <div> so they can be stacked in one
        # page. Neither fragment bundles plotly.js; the page links a local copy
        # from the sibling js/ folder (see the <script> tag and the
        # plotly.min.js write below), so it works offline with no CDN.
        n_scatter = len(fig.data)
        bar_html = bar_fig.to_html(
            include_plotlyjs=False, full_html=False, div_id='barchart',
            default_width='100%', default_height='540px',
            config={'responsive': True, 'doubleClick': False}  # double-click handled below
        )
        scatter_html = fig.to_html(
            include_plotlyjs=False, full_html=False, div_id='scatter3d',
            default_width='100%', default_height='96vh',
            config={'responsive': True}
        )

        # Wire the bar chart up as a clickable legend for the scatter:
        #   single-click a bar -> toggle that cluster on/off
        #   double-click a bar -> isolate that cluster; double-click again -> show all
        # A short timer distinguishes a single click from the first of a double.
        filter_js = """
<script>
(function(){
  var nScatter = __NSCATTER__;
  function wire(){
    var sc = document.getElementById('scatter3d');
    var bar = document.getElementById('barchart');
    if(!sc || !bar || !bar.on){ setTimeout(wire, 200); return; }

    var clickTimer = null, lastIdx = -1, isolated = -1;

    function allIdx(){ var a=[]; for(var k=0;k<nScatter;k++){a.push(k);} return a; }
    function fullOps(){ var a=[]; for(var k=0;k<nScatter;k++){a.push(1.0);} return a; }
    function setBars(ops){ Plotly.restyle(bar, {'marker.opacity':[ops]}, [0]); }

    function singleToggle(i){
      var cur = sc.data[i].visible;
      var hide = (cur === undefined || cur === true);
      Plotly.restyle(sc, {visible: hide ? false : true}, [i]);
      var ops = (bar.data[0].marker.opacity || fullOps()).slice();
      if(!Array.isArray(ops) || ops.length !== nScatter){ ops = fullOps(); }
      ops[i] = hide ? 0.2 : 1.0;          // dim the bar of a hidden cluster
      setBars(ops);
      isolated = -1;
    }

    function doubleIsolate(i){
      if(isolated === i){                       // already isolated -> show all
        Plotly.restyle(sc, {visible: true}, allIdx());
        setBars(fullOps());
        isolated = -1;
      } else {                                  // show only cluster i
        var vis = [], ops = [];
        for(var k=0;k<nScatter;k++){
          vis.push(k === i);
          ops.push(k === i ? 1.0 : 0.2);
        }
        Plotly.restyle(sc, {visible: vis}, allIdx());
        setBars(ops);
        isolated = i;
      }
    }

    bar.on('plotly_click', function(d){
      if(!d || !d.points || !d.points.length) return;
      var i = d.points[0].pointNumber;
      if(clickTimer && lastIdx === i){          // second click on same bar -> double
        clearTimeout(clickTimer); clickTimer = null; lastIdx = -1;
        doubleIsolate(i);
        return;
      }
      if(clickTimer){ clearTimeout(clickTimer); }
      lastIdx = i;
      clickTimer = setTimeout(function(){       // no second click -> single
        clickTimer = null; lastIdx = -1;
        singleToggle(i);
      }, 300);
    });
  }
  wire();
})();
</script>
""".replace("__NSCATTER__", str(n_scatter))

        page_title = (f"{title_prefix} Interactive Visualization "
                      "of Student Queries")
        # Layout: the bar chart sits inside a centred, capped-width column for
        # easy reading, while the 3D scatter breaks out of that column to span
        # most of the viewport (capped so it doesn't look stretched on very
        # wide monitors). The cursor rules make the bars and tick labels read
        # as clickable.
        page_html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>{page_title}</title>"
            # Load plotly.js from the js/ folder beside this HTML before any plot runs
            "<script src='./js/plotly.min.js'></script>"
            "<style>html,body{margin:0;padding:0;background:#fff;"
            "font-family:sans-serif;}"
            ".page{max-width:1400px;margin:0 auto;padding:0 24px 40vh;}"
            "h1.page-title{font-size:28px;font-weight:700;color:#222;"
            "text-align:center;margin:32px 0 38px;}"
            "#scatter3d{margin-top:70px;width:min(96vw,2200px);"
            "position:relative;left:50%;transform:translateX(-50%);}"
            "#barchart,#barchart *{cursor:pointer !important;}"
            "#scatter3d text{cursor:pointer !important;}"
            "</style></head><body>"
            "<div class='page'>"
            f"<h1 class='page-title'>{page_title}</h1>"
            + bar_html + scatter_html +
            "</div>" + filter_js +
            "</body></html>"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"Saved interactive 3D visualization to {output_path}")

        # The page loads plotly.js from a js/ folder beside this HTML (linked
        # above). analyse_data copies that folder in before running; we only
        # check it is present - the HTML and its js/ folder must travel together.
        html_dir = os.path.dirname(os.path.abspath(output_path))
        plotly_js_path = os.path.join(html_dir, "js", "plotly.min.js")
        if not os.path.exists(plotly_js_path):
            print(f"Warning: {plotly_js_path} not found - the page won't render "
                  "until the js/ folder is copied next to the HTML")

    except Exception as e:
        print(f"Error creating interactive plot: {str(e)}")

    return viz_data
