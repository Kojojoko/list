from flask import Flask, jsonify, request, render_template # type: ignore
import requests # type: ignore
import re
import os

app = Flask(__name__)

# Serve the index.html file
@app.route('/')
def index():
    return render_template('./templates/index.html')

def get_vqd_token(query):
    """Retrieve the vqd token required for DuckDuckGo image search."""
    url = "https://duckduckgo.com/?t=h"
    params = {"q": query}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Make a POST request to get the token
    response = requests.post(url, data=params, headers=headers)
    
    # Parse the token from the response
    search_obj = re.search(r'vqd=([\d-]+)\&', response.text, re.M | re.I)
    if not search_obj:
        raise ValueError("Token Parsing Failed!")
    
    return search_obj.group(1)

def search_duckduckgo_images(query):
    """Search DuckDuckGo for images using the vqd token."""
    # Step 1: Append "activity" to the query
    query_with_activity = f"{query} activity"

    # Step 2: Get the vqd token
    vqd = get_vqd_token(query_with_activity)
    
    # Step 3: Use the token to fetch image results
    url = f"https://duckduckgo.com/i.js"
    params = {"q": query_with_activity, "vqd": vqd, "t": "h_", "iax": "images", "ia": "images"}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    
    # Parse the JSON response
    results = response.json()
    if "results" in results and len(results["results"]) > 0:
        return results["results"][0]["image"]  # Return the first image link
    else:
        return "No images found."

@app.route('/get_image', methods=['GET'])
def get_image():
    query = request.args.get('query', default='nike', type=str)
    try:
        image_url = search_duckduckgo_images(query)
        return jsonify({"image_url": image_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Set the template folder to the directory containing index.html
    app.template_folder = os.path.dirname(__file__)
    app.run(debug=True)