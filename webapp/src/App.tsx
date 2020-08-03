import * as React from 'react'
import { BrowserRouter as Router, Route } from 'react-router-dom'
import { GameView, EntryView } from './Pages';
import './style.css';


class App extends React.Component {
    render() {
        return (
            <Router>
                <div>
                    <Route path="/" exact component={EntryView} />
                    <Route path="/:game_id" component={GameView} />
                </div>
            </Router>
        );
    }
}

export default App;
