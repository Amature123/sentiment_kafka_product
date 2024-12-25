import { useState, useEffect } from 'react';
import './App.css';
import { PieChart } from '@mui/x-charts/PieChart';
import { LineChart } from '@mui/x-charts/LineChart';
import {
  Typography,
  List,
  ListItem,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Box,
  Paper,
  Link,
} from '@mui/material';

const API_ENDPOINTS = {
  sentimentSummary: 'http://localhost:8000/stats/sentiment/summary',
  sentimentMessages: 'http://localhost:8000/messages/sentiment',
  sentimentByTime: 'http://localhost:8000/stats/sentiment/iter',
};

function formatSentimentData(data) {
  const totalMessages = data.total_messages ?? 0;
  const positive = totalMessages ? ((data.total_positive / totalMessages) * 100).toFixed(2) : 0;
  const negative = totalMessages ? ((data.total_negative / totalMessages) * 100).toFixed(2) : 0;
  const neutral = totalMessages ? ((data.total_neutral / totalMessages) * 100).toFixed(2) : 0;

  return {
    chartData: [
      { id: 0, value: data.total_positive ?? 0, label: 'Positive' },
      { id: 1, value: data.total_negative ?? 0, label: 'Negative' },
      { id: 2, value: data.total_neutral ?? 0, label: 'Neutral' },
    ],
    summary: {
      totalMessages,
      positive,
      negative,
      neutral,
    },
  };
}

function normalizeSentimentData(dataArray) {
  return dataArray.map(data => {
    const hourDate = new Date(data.check_time);
    const total = data.total_messages;
    return {
      Hour: hourDate,
      positive: total ? Number((data.total_positive_count / total * 100).toFixed(2)) : 0,
      negative: total ? Number((data.total_negative_count / total * 100).toFixed(2)) : 0,
      neutral: total ? Number((data.total_neutral_count / total * 100).toFixed(2)) : 0,
    };
  });
}

function App() {
  const [sentiment, setSentiment] = useState([]);
  const [sentimentSummary, setSentimentSummary] = useState({});
  const [messages, setMessages] = useState([]);
  const [analysisByTime, setAnalysisByTime] = useState([]);

  const fetchData = async (endpoint, processData) => {
    try {
      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error(`Failed to fetch: ${endpoint}`);
      }
      const data = await response.json();
      processData(data);
    } catch (error) {
      console.error(`Error fetching data from ${endpoint}:`, error);
    }
  };

  useEffect(() => {
    const fetchAllData = () => {
      fetchData(API_ENDPOINTS.sentimentSummary, data => {
        const formatted = formatSentimentData(data);
        setSentiment(formatted.chartData);
        setSentimentSummary(formatted.summary);
      });
      fetchData(API_ENDPOINTS.sentimentMessages, data => setMessages(data.messages));
      fetchData(API_ENDPOINTS.sentimentByTime, data => {
        const normalizedData = normalizeSentimentData(data);
        setAnalysisByTime(normalizedData);
      });
    };

    fetchAllData();
    const intervalId = setInterval(fetchAllData, 1000);

    return () => clearInterval(intervalId);
  }, []);

  return (
    <Box sx={{ padding: '2rem', backgroundColor: '#f9f9f9', minHeight: '100vh' }}>
      {/* Summary Boxes */}
      <Box
        sx={{
          display: 'flex',
          gap: '1.5rem',
          marginBottom: '2rem',
          justifyContent: 'space-between',
        }}
      >
        <Paper elevation={3} sx={{ padding: '1rem', flex: 1, textAlign: 'center' }}>
          <Typography variant="h6">Total Messages</Typography>
          <Typography variant="h4">{sentimentSummary.totalMessages || 0}</Typography>
        </Paper>
        <Paper elevation={3} sx={{ padding: '1rem', flex: 1, textAlign: 'center' }}>
          <Typography variant="h6">Positive (%)</Typography>
          <Typography variant="h4">{sentimentSummary.positive || 0}%</Typography>
        </Paper>
        <Paper elevation={3} sx={{ padding: '1rem', flex: 1, textAlign: 'center' }}>
          <Typography variant="h6">Negative (%)</Typography>
          <Typography variant="h4">{sentimentSummary.negative || 0}%</Typography>
        </Paper>
        <Paper elevation={3} sx={{ padding: '1rem', flex: 1, textAlign: 'center' }}>
          <Typography variant="h6">Neutral (%)</Typography>
          <Typography variant="h4">{sentimentSummary.neutral || 0}%</Typography>
        </Paper>
      </Box>

      {/* Main Content */}
      <Box sx={{ display: 'flex', gap: '2rem' }}>
        {/* Left Section */}
        <Box sx={{ flex: 7 }}>
          <Card elevation={3} sx={{ marginBottom: '2rem' }}>
            <CardHeader title="Sentiment Distribution" />
            <Divider />
            <CardContent>
              {sentiment.length > 0 ? (
                <PieChart
                  series={[{ data: sentiment }]}
                  width={600}
                  height={400}
                />
              ) : (
                <Typography>Loading sentiment data...</Typography>
              )}
            </CardContent>
          </Card>

          <Card elevation={3}>
            <CardHeader title="Sentiment Over Time" />
            <Divider />
            <CardContent>
              {analysisByTime.length > 0 ? (
                <LineChart
                  height={400}
                  series={[
                    {
                      data: analysisByTime.map(item => item.positive),
                      label: 'Positive',
                      area: true,
                      stack: 'total',
                      showMark: false,
                    },
                    {
                      data: analysisByTime.map(item => item.negative),
                      label: 'Negative',
                      area: true,
                      stack: 'total',
                      showMark: false,
                    },
                    {
                      data: analysisByTime.map(item => item.neutral),
                      label: 'Neutral',
                      area: true,
                      stack: 'total',
                      showMark: false,
                    },
                  ]}
                  xAxis={[
                    {
                      data: analysisByTime.map(item => item.Hour),
                      scaleType: 'time',
                      valueFormatter: item => item.toLocaleTimeString(),
                    },
                  ]}
                />
              ) : (
                <Typography>Loading time-series data...</Typography>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Right Section */}
        <Box sx={{ flex: 3 }}>
          <Card elevation={3}>
            <CardHeader title="Recent Messages" />
            <Divider />
            <CardContent>
              <List>
                {messages.length > 0 ? (
                  messages.map(item => (
                    <ListItem key={item.id} sx={{ marginBottom: '1rem' }}>
                      <Paper elevation={1} sx={{ padding: '1rem', width: '100%' }}>
                        <Typography variant="body1">
                          <strong>Time:</strong> {new Date(item.latest_post_time).toLocaleString()}
                        </Typography>
                        <Typography variant="body1">
                          <strong>Message:</strong> {item.message_content}
                        </Typography>
                        <Typography variant="body1">
                          <strong>Thread:</strong>{' '}
                          <Link href={item.thread_url} target="_blank" rel="noopener noreferrer">
                            {item.thread_url}
                          </Link>
                        </Typography>
                        <Typography variant="body1">
                          <strong>Sentiment:</strong> {item.sentiment}
                        </Typography>
                      </Paper>
                    </ListItem>
                  ))
                ) : (
                  <Typography>No messages to display.</Typography>
                )}
              </List>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
}

export default App;
