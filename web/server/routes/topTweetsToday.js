const express = require('express');
const router = express.Router();
const topTweetsToday = require('../services/topTweetsToday');

/* GET programming languages. */
router.get('/', async function(req, res, next) {
  try {
    res.json(await topTweetsToday.getMultiple(req.query.page));
  } catch (err) {
    console.error(`Error while getting programming languages `, err.message);
    next(err);
  }
});

module.exports = router;