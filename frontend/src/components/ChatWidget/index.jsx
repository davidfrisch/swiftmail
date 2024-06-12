import { useEffect, useRef } from 'react';

const ChatWidget = () => {
  const iframeRef = useRef(null);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (iframe) {
      // Function to inject the script into the iframe
      const injectScript = () => {
        const doc = iframe.contentDocument || iframe.contentWindow.document;

        // Clear the iframe content
        doc.open();
        doc.write('<!DOCTYPE html><html><head></head><body></body></html>');
        doc.close();

        // Create the script element
        const script = doc.createElement('script');
        script.src = "http://localhost:3001/embed/anythingllm-chat-widget.min.js";
        script.setAttribute('data-embed-id', '931e1e11-da28-4f5e-bdc3-a4993a7cf2df');
        script.setAttribute('data-base-api-url', 'http://localhost:3001/api/embed');
        script.setAttribute('data-open-on-load', 'true');
        script.setAttribute('data-chat-icon', 'support');
        script.setAttribute('data-button-color', 'green');
        script.setAttribute('data-position', 'bottom-left');
        script.setAttribute('data-window-height', '98%');
        script.setAttribute('data-window-width', '98%');
        script.async = true;

        // Append the script to the iframe's body
        doc.body.appendChild(script);
      };

      // Inject the script when the iframe is loaded
      if (iframe.contentWindow) {
        injectScript();
      } else {
        iframe.onload = injectScript;
      }
    }
  }, []);

  return (
    <div style={{width: "100%", height: "100%"}}>
      <iframe ref={iframeRef} style={{ width: '100%', height: '100%', border: 'none' }} title="Chat Widget"></iframe>
    </div>
  );
};

export default ChatWidget;
