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

const anthropic = new Anthropic();
const composio = new Composio({ apiKey: `7szjsin81axmc970di2g`,
  provider: new AnthropicProvider() });

const ME_MD_GRADIENT = "linear-gradient(135deg, #6A5BFF 0%, #00E6D0 100%)";
const ME_MD_ACCENT = "#6A5BFF";
const ME_MD_ACCENT2 = "#00E6D0";
const ME_MD_BG = "linear-gradient(135deg, #181A20 0%, #232526 100%)";
const ME_MD_FONT = "'Inter', 'Segoe UI', 'Arial', sans-serif";

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

    setMessages(prev => [
      ...prev,
      { role: 'assistant', content: response.content[0].type === 'text' ? response.content[0].text : 'Response received' }
    ]);
  }

  const generateQuestion = async () => {
    try {
      const response = await anthropic.messages.create({
        model: "claude-3-haiku-20240307",
        max_tokens: 256,
        messages: [
          { role: 'assistant', content: "You are a tool that wants to learn and infer about a user's preferences based on the website they are on"},
          ...messages,
          { role: 'user', content: `Based on the fact that they are at ${pageInfo?.url} which is a site about ${pageInfo?.title} and the answers given so far, generate a question that is most useful to learn about their preferences for future uses of this website. Only output the question. Make sure that the question is answerable in maximum 3-5 words for the user. Ensure that previous questions don't overlap in subject` }
        ]
      });

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
    e.preventDefault()
    if (!input.trim()) return
    setMessages(prev => [
      ...prev,
      { role: 'user', content: input }
    ]);
    if (messages.length == 2){
      composioSignIn(input.trim())
    }else{
      if (questionCount < 5){
        generateQuestion()
      }else{
        generateInsights()
      }
    }
    setInput('')
  }

  // Me.md logo SVG
  const MeMdLogo = () => (
    <svg width="38" height="38" viewBox="0 0 38 38" fill="none">
      <rect width="38" height="38" rx="12" fill={ME_MD_ACCENT} />
      <path d="M11 27V11H15.5L19 18.5L22.5 11H27V27H23V18.5L19 27L15 18.5V27H11Z" fill="white"/>
    </svg>
  );

  return (
    <div
      style={{
        minHeight: '100vh',
        background: ME_MD_BG,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: ME_MD_FONT,
      }}
    >
      <Container>
        <Row className="justify-content-center">
          <Col xs={12} md={10} lg={8}>
            <Card
              style={{
                background: 'rgba(24, 26, 32, 0.98)',
                border: `2px solid ${ME_MD_ACCENT}`,
                borderRadius: '22px',
                boxShadow: '0 6px 36px 0 rgba(106,91,255,0.10), 0 1.5px 8px 0 rgba(0,230,208,0.08)',
                minHeight: '65vh',
                display: 'flex',
                flexDirection: 'column',
                height: '75vh',
                overflow: 'hidden',
                position: 'relative'
              }}
              className="p-0"
            >
              {/* Header with logo and Me.md branding */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                  padding: '1.2rem 2rem 0.5rem 2rem',
                  borderBottom: `1.5px solid ${ME_MD_ACCENT2}`,
                  background: 'rgba(24,26,32,0.98)',
                  zIndex: 2
                }}
              >
                <MeMdLogo />
                <div>
                  <span style={{
                    fontWeight: 800,
                    fontSize: '1.7rem',
                    letterSpacing: '-0.5px',
                    color: ME_MD_ACCENT,
                    fontFamily: "'Inter', 'Segoe UI', 'Arial', sans-serif"
                  }}>
                    Me.<span style={{color: ME_MD_ACCENT2}}>md</span>
                  </span>
                  <div style={{
                    fontSize: '1.05rem',
                    color: '#b6e9e2',
                    fontWeight: 500,
                    marginTop: '-2px',
                    letterSpacing: '0.01em'
                  }}>
                    Your personal web preference assistant
                  </div>
                </div>
              </div>
              <Card.Body
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  flex: 1,
                  padding: 0,
                  overflow: 'hidden',
                  background: 'transparent'
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
                        color: '#b6e9e2',
                        textAlign: 'center',
                        marginTop: '30%',
                        fontSize: '1.25rem',
                        opacity: 0.8,
                        fontWeight: 500,
                        letterSpacing: '0.01em'
                      }}
                    >
                      👋 Welcome to <span style={{color: ME_MD_ACCENT, fontWeight: 700}}>Me.<span style={{color: ME_MD_ACCENT2}}>md</span></span>!<br />
                      <span style={{fontSize: '1.05rem', color: '#b6e9e2', fontWeight: 400}}>
                        Start a new conversation to personalize your web experience.
                      </span>
                    </div>
                  )}
                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: 'flex',
                        justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        marginBottom: '1.1rem',
                      }}
                    >
                      <div
                        style={{
                          background:
                            msg.role === 'user'
                              ? `linear-gradient(90deg, ${ME_MD_ACCENT2} 0%, ${ME_MD_ACCENT} 100%)`
                              : 'rgba(106,91,255,0.13)',
                          color: msg.role === 'user' ? '#fff' : '#e6eaff',
                          borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                          padding: '0.85rem 1.3rem',
                          maxWidth: '75%',
                          fontSize: '1.08rem',
                          fontWeight: 500,
                          boxShadow: msg.role === 'user'
                            ? '0 2px 8px 0 rgba(0,230,208,0.10)'
                            : '0 2px 8px 0 rgba(106,91,255,0.08)',
                          border: msg.role === 'user'
                            ? `1.5px solid ${ME_MD_ACCENT2}`
                            : `1.5px solid ${ME_MD_ACCENT}22`,
                          wordBreak: 'break-word',
                          whiteSpace: 'pre-line',
                          transition: 'background 0.2s'
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
                    background: 'rgba(24, 26, 32, 0.99)',
                    borderTop: `1.5px solid ${ME_MD_ACCENT2}`,
                    padding: '1.1rem 1.5rem',
                  }}
                >
                  <div style={{ display: 'flex', gap: '0.7rem', alignItems: 'center' }}>
                    <Form.Control
                      type="text"
                      placeholder="Type your message…"
                      value={input}
                      onChange={handleInputChange}
                      style={{
                        background: '#23272f',
                        color: '#fff',
                        border: `1.5px solid ${ME_MD_ACCENT2}`,
                        borderRadius: '10px',
                        fontSize: '1.13rem',
                        fontWeight: 500,
                        boxShadow: 'none',
                        padding: '0.7rem 1.1rem',
                        outline: 'none',
                        transition: 'border 0.2s',
                        fontFamily: ME_MD_FONT
                      }}
                      autoFocus
                    />
                    <Button
                      type="submit"
                      style={{
                        background: ME_MD_GRADIENT,
                        border: 'none',
                        fontWeight: 700,
                        fontSize: '1.13rem',
                        borderRadius: '10px',
                        minWidth: '90px',
                        color: '#fff',
                        boxShadow: '0 2px 8px 0 rgba(106,91,255,0.10)',
                        letterSpacing: '0.01em',
                        transition: 'background 0.2s'
                      }}
                      disabled={!input.trim()}
                    >
                      Send
                    </Button>
                  </div>
                </Form>
              </Card.Body>
              {/* Subtle Me.md watermark */}
              <div
                style={{
                  position: 'absolute',
                  bottom: 10,
                  right: 18,
                  opacity: 0.13,
                  fontWeight: 900,
                  fontSize: '2.2rem',
                  letterSpacing: '-1px',
                  pointerEvents: 'none',
                  userSelect: 'none',
                  color: ME_MD_ACCENT
                }}
              >
                Me.<span style={{color: ME_MD_ACCENT2}}>md</span>
              </div>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  )
}

export default App
