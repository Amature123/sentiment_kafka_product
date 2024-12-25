import { List, ListItem, ListItemText, Typography, Card } from '@mui/material';

const LatestMessages = ({ messages }) => (
  <Card>
    <Typography variant="h6" sx={{ padding: 2 }}>
      Latest Messages
    </Typography>
    <List>
      {messages.map((msg, index) => (
        <ListItem key={index} divider>
          <ListItemText
            primary={msg.content}
            secondary={`Sentiment: ${msg.sentiment}`}
          />
        </ListItem>
      ))}
    </List>
  </Card>
);
export default LatestMessages;
