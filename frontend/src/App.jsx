import "./App.css";
import ChatWidget from "./components/ChatWidget";
import ValidationWidget from "./components/ValidationWidget";
import SaveConversationWidget from "./components/SaveConversationWidget";

function App() {
  return (
    <>
      <div className="container">
        <div className="left-side">
        <ChatWidget />
        </div>
        <div className="right-side">
          <ValidationWidget />
          <SaveConversationWidget />
        </div>
      </div>
    </>
  );
}

export default App;
