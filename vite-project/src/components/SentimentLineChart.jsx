import { Line } from 'react-chartjs-2';
import { Card, CardContent, Typography } from '@mui/material';

const SentimentLineChart = ({ data }) => {
  const chartData = {
    labels: data.timestamps, // e.g., ["10:00", "10:15", "10:30"]
    datasets: [
      {
        label: 'Positive',
        data: data.positive,
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgba(75, 192, 192, 1)',
        fill: true,
      },
      {
        label: 'Neutral',
        data: data.neutral,
        backgroundColor: 'rgba(255, 205, 86, 0.5)',
        borderColor: 'rgba(255, 205, 86, 1)',
        fill: true,
      },
      {
        label: 'Negative',
        data: data.negative,
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgba(255, 99, 132, 1)',
        fill: true,
      },
    ],
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Sentiment Over Time</Typography>
        <Line data={chartData} />
      </CardContent>
    </Card>
  );
};
export default SentimentLineChart;
