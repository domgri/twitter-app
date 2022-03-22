// https://dev.to/pratham10/how-to-set-up-a-node-js-express-server-for-react-2fja

// server/index.js

// const express = require("express");

// const PORT = process.env.PORT || 3001;

// const app = express();

// app.get("/api", (req, res) => {
//     res.json({ message: "Hello from Express!" });
// });
  
// app.listen(PORT, () => {
//     console.log(`Server listening on ${PORT}`);
// });

//https://blog.logrocket.com/build-rest-api-node-express-mysql/

const express = require("express");
const app = express();
const port = 3001;


const topTweetsTodayRouter = require("./routes/topTweetsToday");
const trendingTweetsTodayRouter = require("./routes/trendingTweetsToday");


app.use(express.json());
app.use(
  express.urlencoded({
    extended: true,
  })
);

app.get("/api", (req, res) => {
    res.json({ message: "Hello from Express!" });
});

app.get("/", (req, res) => {
  res.json({ message: "ok" });
});

app.use("/top-tweets-today", topTweetsTodayRouter);

app.use("/trending-tweets-today", trendingTweetsTodayRouter);

/* Error handler middleware */
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  console.error(err.message, err.stack);
  res.status(statusCode).json({ message: err.message });
  return;
});


app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});