import React, { useEffect } from 'react';

const ChatWidget = () => {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = "http://localhost:3001/embed/anythingllm-chat-widget.min.js";
    script.setAttribute('data-embed-id', '931e1e11-da28-4f5e-bdc3-a4993a7cf2df');
    script.setAttribute('data-base-api-url', 'http://localhost:3001/api/embed');
    script.setAttribute('data-open-on-load' , 'true');
    script.setAttribute('data-chat-icon', 'support');
    script.setAttribute('data-button-color', 'green');
    script.setAttribute('data-position', 'bottom-left');
    script.setAttribute('data-window-height', '98%');
    script.setAttribute('data-window-width', '45%');
    script.async = true;
    
    document.body.appendChild(script);

    // Cleanup function to remove the script when the component is unmounted
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div>
      {/* Any other JSX content for your component */}
    </div>
  );
};

export default ChatWidget;
