from dotenv import load_dotenv
import os
import pandas as pd
import requests
import time
import json
import numpy as np
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, normalize
from topic_visualization import create_topic_visualization

prompts_file = "prompts.json"

load_dotenv()

# Azure OpenAI configuration

openai_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT")
openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
llm_deployment_name = os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT")
embedding_deployment_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

openai_headers = {
    "Content-Type": "application/json",
    "api-key": openai_api_key
}

completion_url = f"{openai_endpoint}/openai/deployments/{llm_deployment_name}/chat/completions?api-version={openai_api_version}"
embedding_url = f"{openai_endpoint}/openai/deployments/{embedding_deployment_name}/embeddings?api-version={openai_api_version}"

def get_prompt(prompt_template):
    
    with open(prompts_file,'r') as file:
        templates = json.load(file)
    
    # Get the right prompt template
    return templates.get(prompt_template)

def cosine_kmeans(X_normalized, n_clusters, random_state=42, max_iters=300, n_init=10):
    """
    K-means clustering using cosine similarity instead of Euclidean distance.
    Performs multiple initialisations and returns the best result.
    """

    best_labels = None
    best_inertia = float('inf')
    
    print(f"Running cosine K-means with {n_init} initialisations")
    
    # Multiple random initialisations (like sklearn KMeans)
    for init_run in range(n_init):
        np.random.seed(random_state + init_run)
        
        # Initialise centroids randomly on unit sphere
        centroids = np.random.randn(n_clusters, X_normalized.shape[1])
        centroids = normalize(centroids, norm='l2')
        
        prev_labels = None
        
        for iteration in range(max_iters):
            # Assign points using cosine similarity
            similarities = cosine_similarity(X_normalized, centroids)
            labels = np.argmax(similarities, axis=1)
            
            # Check convergence
            if prev_labels is not None and np.array_equal(labels, prev_labels):
                break
                
            # Update centroids
            new_centroids = []
            for k in range(n_clusters):
                cluster_points = X_normalized[labels == k]
                if len(cluster_points) > 0:
                    centroid = np.mean(cluster_points, axis=0)
                    centroid = normalize(centroid.reshape(1, -1), norm='l2')[0]
                    new_centroids.append(centroid)
                else:
                    # Keep old centroid if no points assigned
                    new_centroids.append(centroids[k])
            
            centroids = np.array(new_centroids)
            prev_labels = labels.copy()
        
        # Calculate inertia using cosine distance (1 - cosine_similarity)
        inertia = 0
        for k in range(n_clusters):
            cluster_mask = labels == k
            if np.sum(cluster_mask) > 0:
                cluster_points = X_normalized[cluster_mask]
                similarities = cosine_similarity(cluster_points, centroids[k].reshape(1, -1))
                cosine_distances = 1 - similarities.flatten()
                inertia += np.sum(cosine_distances)
        
        # Keep best result
        if inertia < best_inertia:
            best_inertia = inertia
            best_labels = labels.copy()
            best_centroids = centroids.copy()
            
        if init_run == 0:  # Print progress on first run
            print(f"Init {init_run + 1}: converged after {iteration + 1} iterations, inertia: {inertia:.4f}")
    
    print(f"Best inertia: {best_inertia:.4f}")
    return best_labels

def perform_clustering(input_path, output_path, n_clusters=50, random_state=42):
    """
    Perform clustering with flexible metric selection using Cosine K-Means
    Uses cosine similarity instead of Euclidean distance for better text embedding clustering.
    """
    
    print(f"Reading data from {input_path}")
    df = pd.read_csv(input_path, usecols=['Id', 'MessageText', 'DateCreated_Message', 'SessionID', 'embedding_vector_json'])
    print(f"Successfully loaded data")
    
    # Parse the embedding vectors from JSON
    print("Parsing embedding vectors")
    df['embedding_vector'] = df['embedding_vector_json'].apply(
        lambda x: np.array(json.loads(x)) if pd.notna(x) else None
    )
    
    # Drop rows with missing embeddings
    valid_df = df.dropna(subset=['embedding_vector']).copy()
    print(f"Found {len(valid_df)} valid entries with embeddings out of {len(df)} total entries")
    
    if len(valid_df) == 0:
        raise ValueError("No valid embeddings found in the dataset.")
    
    if len(valid_df) < n_clusters:
        print(f"Warning: Only {len(valid_df)} entries available, adjusting n_clusters")
        n_clusters = max(2, len(valid_df) // 2)
    
    # Extract vectors into a numpy array for clustering
    X = np.vstack(valid_df['embedding_vector'].values)
    
    # Standardize and L2-normalize the embeddings
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = normalize(X_scaled, norm='l2')

    # Perform cosine K-means clusetering
    final_cluster_labels = cosine_kmeans(
        X_scaled, 
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=10  # Multiple initialisations for best result
    )
    
    clusters_df = valid_df.copy()
    clusters_df['cluster'] = final_cluster_labels
    
    final_clusters_df = clusters_df
    
    # Create a summary of the clusters
    print("Final cluster summary (Cosine K-means):")
    cluster_summary = final_clusters_df.groupby('cluster').size().reset_index(name='count')
    cluster_summary['percentage'] = cluster_summary['count'] / len(final_clusters_df) * 100
    print(cluster_summary)
    
    # Sample a few messages from each cluster for inspection
    print("Sample messages from each cluster:")
    for cluster_id in sorted(final_clusters_df['cluster'].unique()):
        cluster_data = final_clusters_df[final_clusters_df['cluster'] == cluster_id]
        cluster_size = len(cluster_data)
        
        print(f"\nCluster {cluster_id} (size: {cluster_size}):")
        
        if cluster_size == 0:
            print("- No messages found in this cluster")
            continue
        
        # Sample messages (up to 3)
        sample_size = min(3, cluster_size)
        cluster_msgs = cluster_data['MessageText'].sample(n=sample_size, random_state=random_state).tolist()
        
        for msg in cluster_msgs:
            # Truncate long messages for display
            display_msg = f"{msg[:100]}..." if len(msg) > 100 else msg
            print(f"- {display_msg}")
    
    # Use t-SNE for 3D visualization
    print("\nApplying t-SNE for 3D visualization")
    
    tsne = TSNE(
        n_components=3, 
        random_state=random_state
    )

    print(f"Generating t-SNE coordinates for {X_scaled.shape[0]} points")
    X_tsne = tsne.fit_transform(X_scaled)
    
    # Add t-SNE coordinates directly to the clustered data
    clusters_df['tsne_1'] = X_tsne[:, 0]
    clusters_df['tsne_2'] = X_tsne[:, 1]
    clusters_df['tsne_3'] = X_tsne[:, 2]
    
    final_clusters_df = clusters_df
    
    print(f"Successfully generated t-SNE coordinates for {X_scaled.shape[0]} points")

    # Save clusters info to file
    final_clusters_df.to_csv(output_path, index=False)
    print(f"\nSaved Cosine K-means clustering results to {output_path}")
    
    return final_clusters_df

def label_clusters_with_llm(input_path, output_path, max_samples_per_cluster=200):

    clusters_df = pd.read_csv(input_path)

    # Get the number of clusters from the data
    n_clusters = clusters_df['cluster'].nunique()
    print(f"\nGenerating topic labels for {n_clusters} clusters")
    
    # Create a mapping of cluster ID to topic label
    cluster_labels = {}
    
    for cluster_id in clusters_df['cluster'].unique():

        print(f"\nProcessing cluster_id: {cluster_id}")
        
        # Get messages from this cluster (sample to avoid token limits)
        cluster_messages = clusters_df[clusters_df['cluster'] == cluster_id]['MessageText']
        
        # Sample messages
        if len(cluster_messages) > max_samples_per_cluster:
            sampled_messages = cluster_messages.sample(max_samples_per_cluster, random_state=42).tolist()
        else:
            sampled_messages = cluster_messages.tolist()
        
        # Truncate long messages to keep prompt size reasonable
        truncated_messages = [msg[:200] + "..." if len(msg) > 200 else msg for msg in sampled_messages]
        
        # Format messages for the prompt
        formatted_messages = "\n\n---\n\n".join(truncated_messages)
            
        prompt_template = get_prompt("label-clusters")
    
        system_prompt = prompt_template["system"]
        user_prompt = prompt_template["user"].format(formatted_messages=formatted_messages)

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0,
            "max_tokens": 10000
        }
        
        # Make the request with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                
                response = requests.post(completion_url, headers=openai_headers, json=payload)
                response.raise_for_status()
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    topic_label = result["choices"][0]["message"]["content"].strip()
                    # Clean up the label (remove quotes, etc.)
                    topic_label = topic_label.strip('"\'').strip()
                    cluster_labels[cluster_id] = topic_label
                    print(f"Cluster {cluster_id}: '{topic_label}'")
                    break
            
            except Exception as e:
                
                print(f"Error getting topic for cluster {cluster_id}, attempt {attempt+1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(5)  # Wait before retrying
        
        # If all retries failed, assign a default label
        if cluster_id not in cluster_labels:
            cluster_labels[cluster_id] = f"Cluster {cluster_id}"
            
        # Pause to avoid rate limits
        time.sleep(1)
    
    # Save the cluster labels to a file
    label_df = pd.DataFrame({
        'cluster_id': list(cluster_labels.keys()),
        'topic_label': list(cluster_labels.values())
    })
    
    # Add the topic labels to the clusters dataframe and save to file
    clusters_df['topic_label'] = clusters_df['cluster'].map(cluster_labels)
    
    clusters_df.to_csv(output_path, index=False)
    print(f"Saved cluster topic labels")
    
    return clusters_df

def add_embeddings_to_data(input_path, checkpoint_path, output_path, batch_size=10, batch_delay=10):
    
    # Read in the messages
    data_df = pd.read_csv(input_path, header=0, usecols=['Id', 'SessionID', 'IsBot', 'MessageText', 'DateCreated_Message'])

    print(f"\nAdding embeddings to data.")

    message_texts = data_df.MessageText
    embeddings = []

    # Track progress and save periodically
    checkpoint_interval = 50
    failed_indices = []
    
    for i, text in enumerate(message_texts):
        # Handle empty messages
        input_text = text.strip() if isinstance(text, str) else ""
        if not input_text:
            input_text = "empty message"
        
        payload = {
            "input": input_text,
            "encoding_format": "float"
        }
        
        # Retry logic with exponential backoff
        max_retries = 5
        retry_delay = 2
        success = False
        
        for attempt in range(max_retries):
            try:
                response = requests.post(embedding_url, headers=openai_headers, json=payload)
                
                # Check for rate limit (status code 429)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("retry-after", retry_delay))
                    print(f"Rate limit hit for message {i+1}, waiting for {retry_after} seconds (attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                
                result = response.json()
                if "data" in result and len(result["data"]) > 0:
                    vector = result["data"][0]["embedding"]
                    embeddings.append(vector)
                    success = True
                    break
                else:
                    print(f"No embedding data for message {i+1} (attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
            
            except Exception as e:
                print(f"Error for message {i+1}: {str(e)} (attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        
        if not success:
            print(f"Failed after {max_retries} attempts for message {i+1}")
            embeddings.append(None)
            failed_indices.append(i)
        
        # Add a dynamic delay between requests based on batch position
        if (i+1) % batch_size == 0:
            delay = batch_delay  # Delay between batches
            print(f"Progress: Processed message {i+1}")
            time.sleep(delay)
            
        # Periodically save progress
        if (i+1) % checkpoint_interval == 0 or i == len(message_texts) - 1:
            # Create a temporary dataframe with processed data so far
            temp_df = data_df.iloc[:i+1].copy()
            # Add embeddings we have so far, padding with None for the rest
            temp_embeddings = embeddings + [None] * (len(temp_df) - len(embeddings))
            temp_df['embedding_vector_json'] = [json.dumps(vec) if vec is not None else None for vec in temp_embeddings]
            # Save checkpoint
            temp_df.to_csv(checkpoint_path, index=False)
            print(f"Saved checkpoint at message {i+1}")
    
    data_df = data_df.copy()
    data_df['embedding_vector_json'] = [json.dumps(vec) if vec is not None else None for vec in embeddings]
    data_df.to_csv(output_path, index=False)
    
    print(f"Completed: {len(embeddings)} total, {len(failed_indices)} failed")

def main():

    data = "files/test_data.csv"
    data_checkpoint = "files/test_data_checkpoint.csv"
    data_embeddings = "files/test_data_with_embeddings.csv"
    data_clusters = "files/test_data_with_clusters.csv"
    data_labeled_clusters = "files/test_data_with_labeled_clusters.csv"
    visualization = "files/test_visualization.html"

    add_embeddings_to_data(data, data_checkpoint, data_embeddings, 10, 10)
    perform_clustering(data_embeddings, data_clusters, 42)
    label_clusters_with_llm(data_clusters, data_labeled_clusters, 100
    create_topic_visualization(data_labeled_clusters, visualization)

if __name__ == "__main__":
    main()