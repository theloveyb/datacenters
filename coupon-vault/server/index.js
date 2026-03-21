const express = require('express');
const cors = require('cors');
const Anthropic = require('@anthropic-ai/sdk');

const app = express();
app.use(cors());
app.use(express.json({ limit: '10mb' }));

const anthropic = new Anthropic.default();

const PORT = process.env.PORT || 3001;

app.post('/extract', async (req, res) => {
  const { type, content, prompt } = req.body;

  if (!content || !prompt) {
    return res.status(400).json({ error: 'Missing content or prompt' });
  }

  try {
    const messages = [];

    if (type === 'image') {
      messages.push({
        role: 'user',
        content: [
          {
            type: 'image',
            source: {
              type: 'base64',
              media_type: 'image/jpeg',
              data: content,
            },
          },
          {
            type: 'text',
            text: prompt,
          },
        ],
      });
    } else {
      messages.push({
        role: 'user',
        content: [
          {
            type: 'text',
            text: `${prompt}\n\n--- BEGIN COUPON CONTENT ---\n${content}\n--- END COUPON CONTENT ---`,
          },
        ],
      });
    }

    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 2048,
      messages,
    });

    const responseText = response.content
      .filter((block) => block.type === 'text')
      .map((block) => block.text)
      .join('');

    // Extract JSON from the response (handle markdown code blocks)
    const jsonMatch = responseText.match(/```(?:json)?\s*([\s\S]*?)```/) || [null, responseText];
    const jsonStr = (jsonMatch[1] || responseText).trim();

    const parsed = JSON.parse(jsonStr);

    res.json(parsed);
  } catch (error) {
    console.error('Extraction error:', error.message);
    res.status(500).json({
      error: 'Extraction failed',
      coupons: [],
    });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => {
  console.log(`Coupon extraction server running on port ${PORT}`);
});
