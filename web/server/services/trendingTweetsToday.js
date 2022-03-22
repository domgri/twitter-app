const db = require('./db');
const helper = require('../helper');
const config = require('../config');

async function getMultiple(page = 1){
  const offset = helper.getOffset(page, config.listPerPage);
  // const rows = await db.query(
  //   `SELECT id, favouriteCount
  //   FROM trending_tweets LIMIT ${offset},${config.listPerPage}`
  // );
  const rows = await db.query(
    `SELECT id, favouriteCount from trending_tweets
     ORDER BY favouriteCount DESC
     LIMIT 5 OFFSET 5`);
  const data = helper.emptyOrRows(rows);
  const meta = {page};

  return {
    data,
    meta
  }
}

module.exports = {
  getMultiple
}