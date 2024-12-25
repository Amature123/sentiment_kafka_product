import { CircularProgress, Typography, Box } from '@mui/material';

const SentimentGauge = ({ sentiment }) => {
  const colorMap = {
    Positive: 'success.main',
    Neutral: 'warning.main',
    Negative: 'error.main',
  };

  return (
    <Box textAlign="center">
      <CircularProgress
        variant="determinate"
        value={sentiment.score * 100} // e.g., 0.8 -> 80%
        color={colorMap[sentiment.label]}
        size={120}
        thickness={6}
      />
      <Typography variant="h6" mt={2}>
        Current Sentiment: {sentiment.label}
      </Typography>
    </Box>
  );
};
export default SentimentGauge;
