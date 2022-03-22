const express = require('express');
const router = express.Router();
const trendingTweetsToday = require('../services/trendingTweetsToday');

/* GET programming languages. */
router.get('/', async function(req, res, next) {
  try {
    res.json(await trendingTweetsToday.getMultiple(req.query.page));
  } catch (err) {
    console.error(`Error while getting programming languages `, err.message);
    next(err);
  }
});

module.exports = router;