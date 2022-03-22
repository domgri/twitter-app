const config = {
    db: {
      /* don't expose password or any sensitive info, done only for demo */
      // TODO: dont expose lol
      host: "mysql",
      port: "3306",
      user: "client_01",
      password: "goodLuckBruteForcingTh1sB@byB0Y!",
      database: "tweets_with_counts",
    },
    listPerPage: 10,
  };
  module.exports = config;
