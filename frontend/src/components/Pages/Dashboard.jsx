import React from 'react';
import { 
  Container, Grid, Typography, Box 
} from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';

const BenefitItem = ({ children }) => (
  <Box sx={{ display: 'flex', alignItems: 'start', mb: 2 }}>
    {children}
  </Box>
);

const Dashboard = () => {
  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Box sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Transform Your Documents with Advanced AI
            </Typography>
            
            <Typography variant="body1" paragraph>
              Our document processing technology leverages cutting-edge AI to analyze and enhance your written content, delivering professional-grade improvements in clarity, structure, and impact.
            </Typography>

            <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2, mt: 3 }}>
              How It Works:
            </Typography>

            <BenefitItem>
              <CheckCircleOutlineIcon color="primary" sx={{ mr: 1 }} />
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                  Intelligent Analysis
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Our system performs comprehensive linguistic analysis to understand context, tone, and purpose.
                </Typography>
              </Box>
            </BenefitItem>

            <BenefitItem>
              <CheckCircleOutlineIcon color="primary" sx={{ mr: 1 }} />
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                  Enhanced Readability
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Receive targeted suggestions to improve sentence structure, eliminate redundancies, and enhance overall flow.
                </Typography>
              </Box>
            </BenefitItem>

            <BenefitItem>
              <CheckCircleOutlineIcon color="primary" sx={{ mr: 1 }} />
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                  Grammar Perfection
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Advanced grammatical review identifies and corrects errors that standard tools miss.
                </Typography>
              </Box>
            </BenefitItem>

            <BenefitItem>
              <CheckCircleOutlineIcon color="primary" sx={{ mr: 1 }} />
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                  Style Optimization
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Tailored recommendations ensure your document achieves its intended purpose with maximum impact.
                </Typography>
              </Box>
            </BenefitItem>

            <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic' }}>
              Trusted by professionals across industries for developing high-stakes communications, reports, and content that demands precision and clarity.
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
