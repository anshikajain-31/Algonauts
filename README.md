# News Scraper & React Frontend

This repository contains a **news scraping and summarization** script (`news_scraper.py`) and a **React frontend** that displays categorized news articles by fetching data via an AWS-based backend.

## 🔗 Connection Flow
1️⃣ **React Frontend (VSCode)**  
- Runs on your local machine.
- Calls the AWS API Gateway URL to fetch categorized news (e.g., `https://isegp27f20.execute-api.eu-north-1.amazonaws.com/news?category=politics`).

2️⃣ **AWS API Gateway**  
- Receives the request from React.
- Forwards it to the AWS Lambda function.

3️⃣ **AWS Lambda (Backend Logic)**  
- Extracts the requested category from the query parameters.
- Queries MongoDB for matching news.

4️⃣ **MongoDB (news_database)**  
- Stores the news data.
- Returns matching documents (or an empty list `[]` if no matches are found).

5️⃣ **AWS Lambda Response**  
- Converts the MongoDB query result into a JSON response.
- Sends it back to React via API Gateway.

6️⃣ **React UI Updates**  
- Receives the JSON response.
- Updates the UI with the fetched news articles.

---

## 📂 Project Structure
```
📁 news-scraper-project/
│── 📁 frontend/          # React frontend
│   ├── src/             # React source code
│   ├── package.json     # React dependencies
│   ├── ...
│
│── 📁 backend/          # Backend (AWS Lambda & MongoDB)
│   ├── news_scraper.py  # Web scraping & summarization script
│   ├── lambda_handler.py # AWS Lambda function
│   ├── server.js        # Express.js server for handling API requests
│
│── requirements.txt     # Python dependencies
│── README.md            # Project Documentation
```

---

## 🚀 How to Run the Project

### 1️⃣ Setting up the Backend
#### Prerequisites:
- **Python 3.x**
- **MongoDB Atlas or Local MongoDB**
- **AWS Lambda & API Gateway Setup**
- **Required Python packages** (install using `pip`):
  ```bash
  pip install -r requirements.txt
  ```
- Ensure **PyTorch** is installed for `transformers`:
  ```bash
  pip install torch
  ```
  Or refer to [PyTorch installation guide](https://pytorch.org/get-started/) for specific OS installation.

#### Steps:
1. Update `news_scraper.py` with the desired city/category filters.
2. Deploy `lambda_handler.py` as an AWS Lambda function.
3. Ensure API Gateway is correctly configured to forward requests to the Lambda function.
4. Verify MongoDB is accessible and populated with news data.

![AWS Lambda Function Overview](attachment://image.png)

---

### 2️⃣ Running the Frontend
#### Prerequisites:
- **Node.js & npm installed**

#### Steps:
1. Navigate to the `frontend/` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the React development server:
   ```bash
   npm start
   ```
4. Open `http://localhost:3000` in your browser.

---

### 3️⃣ Running the Backend Locally (Optional)
If you are using `server.js` for API handling instead of AWS Lambda, follow these steps:
1. Navigate to the `backend/` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. If dependencies are missing, install them manually:
   ```bash
   npm install express cors dotenv mongoose
   ```
4. Create a `.env` file in the `backend/` directory and add:
   ```
   MONGO_URI=mongodb+srv://your-mongo-url
   PORT=5000
   ```
5. Start the server:
   ```bash
   node server.js
   ```
6. The API should now be available at `http://localhost:5000`.

---

## 🔧 Customization
- **Modify `news_scraper.py`** to scrape news from different sources or summarize based on different criteria.
- **Adjust MongoDB queries** in `lambda_handler.py` to refine the filtering logic.
- **Update API Gateway URL** in the React frontend (`src/config.js` or similar) to match your deployment.

---

## 🛠 Future Enhancements
- Add support for multiple news sources.
- Implement authentication for API requests.
- Improve UI/UX with better filtering and sorting.

---

## 📜 License
This project is licensed under [MIT License](LICENSE).

---

## 💡 Contributing
Feel free to open issues and pull requests to enhance the project!

