import { useState, useRef, useEffect } from 'react'
import { Container, Card, Row, Col, Form, Button } from 'react-bootstrap'
import { Composio } from '@composio/core';
import { AnthropicProvider } from '@composio/anthropic';
import Anthropic from '@anthropic-ai/sdk';
import 'bootstrap/dist/css/bootstrap.min.css'
import './App.css'

// Chrome extension types
declare global {
  interface Window {
    chrome?: {
      runtime?: {
        sendMessage?: (message: any, callback?: (response: any) => void) => void;
      };
    };
  }
}


const anthropic = new Anthropic({
  apiKey: `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`,
  dangerouslyAllowBrowser: true 
});
const composio = new Composio({ apiKey: `7szjsin81axmc970di2g`,
  provider: new AnthropicProvider() });



function App() {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([])
  const [input, setInput] = useState('')
  const [questionCount, setQuestionCount] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)
  // const [signedIn, setSignedIn] = useState(false)
  const [pageInfo, setPageInfo] = useState<{ title: string; url: string } | null>(null)

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Get page info when component mounts
  useEffect(() => {
    const getPageInfo = async () => {
      try {
        // Check if we're in a Chrome extension context
        if (typeof window !== 'undefined' && window.chrome?.runtime?.sendMessage) {
          window.chrome.runtime.sendMessage({ action: 'getPageInfo' }, (response: any) => {
            if (response && response.title && response.url) {
              setPageInfo(response);
              console.log(response, pageInfo)
              // Add page info to messages
              setMessages(prev => [
                ...prev,
                { 
                  role: 'assistant', 
                  content: `Current page: ${response.title}`
                }
              ]);
            }
          });
        }
      } catch (error) {
        console.log('Not in extension context or error getting page info:', error);
      }
    };

    getPageInfo();
  }, []);


  const composioSignIn = async (email:string) => {
    
    
    const connection = await composio.toolkits.authorize(email, 'google');

    setMessages(prev => [
      ...prev,
      { role: 'assistant', content: `🔗 Visit the URL to authorize:\n👉 ${connection.redirectUrl}` }
    ]);

    // const tools = await composio.tools.get(email, { toolkits: ['LINEAR'] });
    await connection.waitForConnection();
  }

  const generateInsights = async () => {
    
    const response = await anthropic.messages.create({
      model: "claude-3-haiku-20240307",
      max_tokens: 256,
      messages: [
        { role: 'assistant', content: "You are Sherlock Holmes from the BBC show who uses these observations to think through a user's preferences and motivations for this website."},
        ...messages,
        { role: 'user', content: `Using the answers and questions from this interaction, make inferences and analyze the user's preferences. Use these keywords 'dietary': {
                'vegetarian', 'vegan', 'allergy', 'allergic', 'spicy', 'mild', 
                'meat', 'dairy', 'gluten', 'diet', 'dietary'
            },
            'cuisine': {
                'asian', 'mexican', 'thai', 'chinese', 'indian', 'italian', 
                'japanese', 'vietnamese', 'cuisine', 'food', 'restaurant'
            },
            'budget': {
                'cheap', 'expensive', 'budget', 'price', 'cost', 'affordable',
                '$', '$$', '$$$', 'money', 'spend'
            },
            'location': {
                'near', 'close', 'distance', 'neighborhood', 'area', 'transit',
                'walk', 'drive', 'uber', 'bart', 'muni'
            },
            'timing': {
                'time', 'when', 'available', 'reservation', 'book', 'table',
                'tonight', 'tomorrow', 'weekend', 'lunch', 'dinner', 'breakfast'
            } and output with these choices in a json format. Remove the preamble and conclusion and only output the JSON` }
      ]
    });
    console.log(response)
    setMessages(prev => [
      ...prev,
      { role: 'assistant', content: response.content[0].type === 'text' ? response.content[0].text : 'Response received' }
    ]);
  }

  const generateQuestion = async () => {

  // Call Anthropic API to generate assistant reply
  try {
    // Prepare the Anthropic API call with system and user prompt
    // (Assumes anthropic and messages, pageInfo are in scope)

    const response = await anthropic.messages.create({
      model: "claude-3-haiku-20240307",
      max_tokens: 256,
      messages: [
        { role: 'assistant', content: "You are a tool that wants to learn and infer about a user's preferences based on the website they are on"},
        ...messages,
        { role: 'user', content: `Based on the fact that they are at ${pageInfo?.url} which is a site about ${pageInfo?.title} and the answers given so far, generate a question that is most useful to learn about their preferences for future uses of this website. Only output the question. Make sure that the question is answerable in maximum 3-5 words for the user. Ensure that previous questions don't overlap in subject` }
      ]
    });

    console.log(response)

    setMessages(prev => [
      ...prev,
      { role: 'assistant', content: response.content[0].type === 'text' ? response.content[0].text : 'Response received' }
    ]);
    setQuestionCount(questionCount + 1)
  } catch (error) {
    setMessages(prev => [
      ...prev,
      { role: 'assistant', content: "Sorry, there was an error generating a response." }
    ]);
  }


  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const handleSend = (e: React.FormEvent) => {
    console.log(messages)
    e.preventDefault()
    if (!input.trim()) return
    // Add the user's message to the chat
    setMessages(prev => [
      ...prev,
      { role: 'user', content: input }
    ]);
    if (messages.length == 0){
      composioSignIn(input.trim())
    }else{
      if (questionCount < 2){
        generateQuestion()
      }else{
        generateInsights()
      }
    }
    setInput('')
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #232526 0%, #0f2027 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Container>
        <Row className="justify-content-center">
          <Col xs={12} md={10} lg={8}>
            <Card
              style={{
                background: 'rgba(30, 30, 30, 0.95)',
                border: 'none',
                borderRadius: '18px',
                boxShadow: '0 4px 32px 0 rgba(0,0,0,0.25)',
                minHeight: '60vh',
                display: 'flex',
                flexDirection: 'column',
                height: '70vh',
              }}
              className="p-0"
            >
              <Card.Body
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  flex: 1,
                  padding: 0,
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    flex: 1,
                    overflowY: 'auto',
                    padding: '2rem 1.5rem 1rem 1.5rem',
                    background: 'transparent',
                  }}
                >
                  {messages.length === 0 && (
                    <div
                      style={{
                        color: '#bbb',
                        textAlign: 'center',
                        marginTop: '30%',
                        fontSize: '1.2rem',
                        opacity: 0.7,
                      }}
                    >
                      Start a new conversation
                    </div>
                  )}
                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: 'flex',
                        justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        marginBottom: '1rem',
                      }}
                    >
                      <div
                        style={{
                          background:
                            msg.role === 'user'
                              ? 'linear-gradient(90deg, #00c97b 0%, #00d4ff 100%)'
                              : '#23272f',
                          color: msg.role === 'user' ? '#fff' : '#eee',
                          borderRadius: '12px',
                          padding: '0.75rem 1.2rem',
                          maxWidth: '70%',
                          fontSize: '1.05rem',
                          boxShadow: msg.role === 'user'
                            ? '0 2px 8px 0 rgba(0,201,123,0.10)'
                            : '0 2px 8px 0 rgba(0,0,0,0.10)',
                        }}
                      >
                        {msg.content}
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
                <Form
                  onSubmit={handleSend}
                  style={{
                    background: 'rgba(20, 20, 20, 0.98)',
                    borderTop: '1px solid #333',
                    padding: '1rem 1.5rem',
                  }}
                >
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <Form.Control
                      type="text"
                      placeholder="Send a message..."
                      value={input}
                      onChange={handleInputChange}
                      style={{
                        background: '#23272f',
                        color: '#fff',
                        border: '1px solid #444',
                        borderRadius: '8px',
                        fontSize: '1.1rem',
                        boxShadow: 'none',
                      }}
                      autoFocus
                    />
                    <Button
                      type="submit"
                      variant="success"
                      style={{
                        background: 'linear-gradient(90deg, #00c97b 0%, #00d4ff 100%)',
                        border: 'none',
                        fontWeight: 600,
                        fontSize: '1.1rem',
                        borderRadius: '8px',
                        minWidth: '90px',
                      }}
                      disabled={!input.trim()}
                    >
                      Send
                    </Button>
                  </div>
                </Form>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  )
}

export default App
