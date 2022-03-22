import React from "react";
import logo from './logo.svg';
import './App.css';
import { Tweet } from 'react-twitter-widgets'

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';

import 'bootstrap/dist/css/bootstrap.min.css';

function App() {

  const [topTweetsToday, setTopTweetsToday] = React.useState(null);
  const [trendingTweetsToday, setTrendingTweetsToday] = React.useState(null);


  React.useEffect(() => {
    
    fetch("/top-tweets-today")
      .then((res) => res.json())
      .then((topTweetsToday) => setTopTweetsToday(topTweetsToday.data));

    fetch("/trending-tweets-today")
      .then((res) => res.json())
      .then((trendingTweetsToday) => setTrendingTweetsToday(trendingTweetsToday.data));
      
  }, []);


  

  return (
    <div className="App">
      {/* <header className="App-header"> */}
        {/* <img src={logo} className="App-logo" alt="logo" /> */}


        {/* {!data ? "Loading..." : data.map( ({id, favouriteCount}) => {return <p key={id}>{id}</p>})} */}
        
        {/* <Tweet tweetId="841418541026877441" /> */}


        {/* <p>{!data ? "Loading..." : data}</p> */}
        {/* <p>{data.map((i) => { return i.id})}</p> */}
        
        {/* <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a> */}
      {/* </header> */}
      <Container >
      <Row className="RowHeader">
        <Col >Tags: #StandWithUkraine</Col>
        <Col >Header text / logo</Col>
        <Col >
          <Button variant="outline-primary">Button1</Button>
          <Button variant="outline-primary">Button2</Button>
          <Button variant="outline-primary">Button3</Button>
        </Col>
       
      </Row>
      <Row>
      <Container >
        <Row className="RowContext">
          <Col className="ColContext" md={{order: 1}} lg={4}>
            <div className="RowName"> Top tweets 24h </div>
            {!topTweetsToday ? "Loading..." : topTweetsToday.map( ({id, favouriteCount}) => {return <Tweet tweetId={id} />})}
          </Col>
          <Col className="ColContext" md={{order: 2}} lg={4}>
          <div className="RowName"> Trending tweets today</div>
            {!trendingTweetsToday ? "Loading..." : trendingTweetsToday.map( ({id, favouriteCount}) => {return <Tweet tweetId={id} />})}
          </Col>
          <Col className="ColContext" md={{order: 3}} lg={4}>
          <div className="RowName"> Trending tweets last hour</div>
            {!trendingTweetsToday ? "Loading..." : trendingTweetsToday.map( ({id, favouriteCount}) => {return <Tweet tweetId={id} />})}
          </Col>
        </Row>
      </Container>
      </Row>
      <Row>Footer</Row>
      </Container>
     
      
      
    </div>
  );
}

export default App;
