import pandas as pd
import plotly.express as px
import pytz


def create_topic_visualization(input_path, output_path):
    
    print("Preparing 3D visualization of labeled topics")

    clustered_data = pd.read_csv(input_path)

    # Get the cluster information
    clusters = sorted(clustered_data['cluster'].unique())
    
    # Count sizes of each cluster and create ordered information
    cluster_sizes = clustered_data['cluster'].value_counts().to_dict()
    
    # Create topic labels with size information AND ensure uniqueness
    topic_labels = {}
    used_labels = set()
    
    for cluster in clusters:
        if 'topic_label' in clustered_data.columns:
            topic_label = clustered_data[clustered_data['cluster'] == cluster]['topic_label'].iloc[0]
            
            # Handle missing/NaN topic labels
            if pd.isna(topic_label) or topic_label == '' or topic_label is None:
                topic_label = f"Cluster {cluster}"
        else:
            topic_label = f"Cluster {cluster}"
        
        topic_size = cluster_sizes.get(cluster, 0)
        
        # Make the label unique by adding cluster ID if needed
        base_label = f"{topic_label} (size: {topic_size})"
        unique_label = base_label
        
        # If this label already exists, add cluster ID to make it unique
        if unique_label in used_labels:
            unique_label = f"{topic_label} [Cluster {cluster}] (size: {topic_size})"
            
        # If still not unique (very rare), add a counter
        counter = 1
        while unique_label in used_labels:
            unique_label = f"{topic_label} [Cluster {cluster}-{counter}] (size: {topic_size})"
            counter += 1
        
        topic_labels[cluster] = unique_label
        used_labels.add(unique_label)
    
    print(f"Created {len(topic_labels)} unique topic labels")
    
    # Create ordered clusters by size (largest first)
    clusters_by_size = sorted(clusters, key=lambda x: cluster_sizes.get(x, 0), reverse=True)
    
    if 'tsne_1' in clustered_data.columns and 'tsne_2' in clustered_data.columns and 'tsne_3' in clustered_data.columns:
        clustered_data['has_viz'] = clustered_data['tsne_1'].notna()
        print(f"Found t-SNE coordinates for {clustered_data['has_viz'].sum()} points")
    
    # Filter to points with visualisation coordinates
    viz_data = clustered_data[clustered_data['has_viz']].copy()
    if len(viz_data) == 0:
        print("Error: No points have visualisation coordinates. Cannot create visualisation")
        return clustered_data
    
    print(f"Visualising {len(viz_data)} points across {len(clusters)} topics")
    
    # Calculate axis bounds for fixed scaling
    x_min, x_max = viz_data['tsne_1'].min(), viz_data['tsne_1'].max()
    y_min, y_max = viz_data['tsne_2'].min(), viz_data['tsne_2'].max()
    z_min, z_max = viz_data['tsne_3'].min(), viz_data['tsne_3'].max()

    # Add 5% padding to each axis
    x_range = x_max - x_min
    y_range = y_max - y_min
    z_range = z_max - z_min
    x_min -= 0.025 * x_range
    x_max += 0.025 * x_range
    y_min -= 0.025 * y_range
    y_max += 0.025 * y_range
    z_min -= 0.025 * z_range
    z_max += 0.025 * z_range
    
    # Create interactive Plotly 3D visualization
    try:
        print("Creating interactive 3D visualization")
        
        # Add a combined field for visualization with unique topic name and size
        viz_data['topic_name'] = viz_data['cluster'].apply(
            lambda x: topic_labels.get(x, f'Cluster {x}')
        )
        
        # Create unique ordered categories for the legend (by size)
        ordered_categories = [topic_labels.get(c, f'Cluster {c}') for c in clusters_by_size]
        
        # Verify categories are unique before creating categorical
        if len(ordered_categories) != len(set(ordered_categories)):
            print("Warning: Found duplicate categories.")
            print("Duplicate categories:", [cat for cat in ordered_categories if ordered_categories.count(cat) > 1])
            # Force uniqueness as last resort
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
        
        # Now safely convert to categorical
        viz_data['topic_name'] = pd.Categorical(
            viz_data['topic_name'],
            categories=ordered_categories,
            ordered=True
        )
        
        # Create a truncated message preview for hover data
        viz_data['message_preview'] = viz_data['MessageText'].apply(
            lambda text: text[:200] + "..." if len(text) > 200 else text
        )
        
        # Create a formatted date string for hover information with Dublin timezone
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

        hover_data = {
            'topic_name': True,
            'message_preview': True,
            'formatted_date': True,
            'cluster': True,
            'SessionID': True,
            'Id': True,
            'tsne_1': False,  # Hide x coordinate
            'tsne_2': False,  # Hide y coordinate
            'tsne_3': False   # Hide z coordinate
        }
        
        # Create the 3D scatter plot with timestamp in hover data
        fig = px.scatter_3d(
            viz_data, 
            x='tsne_1', 
            y='tsne_2', 
            z='tsne_3',
            color='topic_name',
            hover_data=hover_data,
            opacity=0.7,
            title=f'<b>3D Visualization of {len(clusters)} Cluster Topics in Student Queries</b>',
            color_discrete_sequence=px.colors.qualitative.Bold,
            category_orders={'topic_name': ordered_categories}  # Force the legend order
        )
        
        # Fixed axes layout with locked scale
        fig.update_layout(
            legend_title_text='<b>Cluster Topics (by size = # user messages)</b>',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.99,
                traceorder='normal',
                font=dict(size=14)
            ),
            scene=dict(
                xaxis_title='t-SNE Dimension 1',
                yaxis_title='t-SNE Dimension 2',
                zaxis_title='t-SNE Dimension 3',
                # Lock the axis ranges to prevent auto-scaling
                xaxis=dict(range=[x_min, x_max]),
                yaxis=dict(range=[y_min, y_max]),
                zaxis=dict(range=[z_min, z_max]),
                # Disable auto-scaling on legend interactions
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=1)
            ),
            margin=dict(l=5, r=5, b=5, t=40)
        )
        
        # Custom hover styling
        fig.update_traces(
            marker=dict(
                size=5,              
                line=dict(width=0) # No outline around points
            ),
            hovertemplate =
                '<b>Topic:</b> %{customdata[0]}<br>' +
                '<b>Preview Message:</b> %{customdata[1]}<br>' +
                '<b>Date:</b> %{customdata[2]}<br>' +
                '<b>Cluster ID:</b> %{customdata[3]}<br>' +
                '<b>Session ID:</b> %{customdata[4]}<br>' +
                '<b>Message ID:</b> %{customdata[5]}<extra></extra>'
        )
        
        # Apply hover styling to each trace individually to ensure colors work properly
        for trace in fig.data:
            trace.update(
                hoverlabel=dict(
                    bgcolor="white",
                    font=dict(color="black", size=14),
                    bordercolor=trace.marker.color
                )
            )
        
        # Save as interactive HTML without navigation buttons
        fig.write_html(output_path)
        print(f"Saved interactive 3D visualization to {output_path}")
        
    except Exception as e:
        print(f"Error creating interactive plot: {str(e)}")
    
    return viz_data