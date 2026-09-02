const express = require('express');
const crypto = require('crypto');
const app = express();

app.use(express.json());

// ၁။ App စတင်ဖွင့်ချိန်တွင် Device Status စစ်ဆေးခြင်း
app.post('/api/check-device-status', async (req, res) => {
  const { deviceId, sessionToken } = req.body;
  
  return res.json({
    status: 'NEW_DEVICE',
    message: 'Free Key နှင့် ကြော်ငြာ ၂ ပုဒ် ကြည့်ရန် လိုအပ်ပါသည်။'
  });
});

// ၂။ Telegram Mini App ထဲမှ ပထမဆုံးအကြိမ် ကြော်ငြာ ကြည့်ပြီးပါက Free Key ထုတ်ပေးခြင်း
app.post('/api/activate-first-time-free', async (req, res) => {
  const { deviceId, adsVerified } = req.body;

  if (!adsVerified) {
    return res.status(400).json({ success: false, message: 'ကြော်ငြာ ၂ ပုဒ် အပြည့် ကြည့်ရန် လိုအပ်ပါသည်။' });
  }

  const sessionToken = crypto.randomBytes(20).toString('hex');

  res.json({
    success: true,
    sessionToken,
    remainingDays: 30,
    message: 'Free Key အသက်သွင်းပြီးပါပြီ။'
  });
});

// ၃။ App ပြန်ဝင်တိုင်း ကြော်ငြာ စစ်ဆေးပေးခြင်း
app.post('/api/verify-session-ads', async (req, res) => {
  const { deviceId, adsVerified } = req.body;

  if (!adsVerified) {
    return res.status(400).json({ success: false, message: 'ကြော်ငြာ ၂ ပုဒ် ပြည့်အောင် ကြည့်ပေးပါ။' });
  }

  const sessionToken = crypto.randomBytes(20).toString('hex');

  res.json({
    success: true,
    sessionToken,
    message: 'Session အတည်ပြုပြီးပါပြီ။ App ထဲသို့ ဝင်ရောက်နိုင်ပါပြီ။'
  });
});

module.exports = app;
    if (!user) {
      user = new DeviceUser({
        deviceId,
        trialStartDate: now,
        trialEndDate: expiryDate
      });
    } else {
      // Re-install သို့မဟုတ် Data Clear လုပ်ထားလျှင် မူလ သက်တမ်းအတိုင်းသာ ထိန်းထားမည်
      if (!user.trialStartDate) {
        user.trialStartDate = now;
        user.trialEndDate = expiryDate;
      }
    }

    // Session Token အသစ် ထုတ်ပေးခြင်း
    const sessionToken = crypto.randomBytes(20).toString('hex');
    user.sessionToken = sessionToken;
    user.sessionExpiresAt = new Date(now.getTime() + 12 * 60 * 60 * 1000); // 12hr Session
    await user.save();

    res.json({
      success: true,
      sessionToken,
      remainingDays: Math.ceil((user.trialEndDate - now) / (1000 * 60 * 60 * 24)),
      message: 'Free Key အသက်သွင်းပြီးပါပြီ။'
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ၃။ App ပြန်ဝင်တိုင်း (Session သစ်အတွက်) ကြော်ငြာ ၂ ပုဒ် ကြည့်ပြီးကြောင်း စစ်ဆေးပေးခြင်း (Key ထပ်ထည့်ရန် မလို)
router.post('/api/verify-session-ads', async (req, res) => {
  const { deviceId, adsVerified } = req.body;

  if (!adsVerified) {
    return res.status(400).json({ success: false, message: 'ကြော်ငြာ ၂ ပုဒ် ပြည့်အောင် ကြည့်ပေးပါ။' });
  }

  try {
    const user = await DeviceUser.findOne({ deviceId });
    if (!user) {
      return res.status(404).json({ success: false, message: 'Device မတွေ့ရှိပါ။' });
    }

    const now = new Date();
    const sessionToken = crypto.randomBytes(20).toString('hex');

    user.sessionToken = sessionToken;
    user.sessionExpiresAt = new Date(now.getTime() + 12 * 60 * 60 * 1000); // Session ၁၂ နာရီ ဖွင့်ပေးထားမည်
    await user.save();

    res.json({
      success: true,
      sessionToken,
      message: 'Session အတည်ပြုပြီးပါပြီ။ App ထဲသို့ ဝင်ရောက်နိုင်ပါပြီ။'
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
// ==========================================
// Adsgram Reward Callback Endpoint
// ==========================================
app.get('/api/reward', async (req, res) => {
    try {
        const userId = req.query.userId;
        
        if (!userId) {
            return res.status(400).json({ 
                success: false, 
                message: 'Missing userId parameter' 
            });
        }

        // TODO: ဒီနေရာမှာ Database ထဲက သက်ဆိုင်ရာ userId ကို Key တစ်ခု တိုးပေးမယ့် ကုဒ်ထည့်ရန်
        console.log(`Success: User ${userId} watched the ad and earned a key.`);

        return res.status(200).json({ 
            success: true, 
            message: 'Key rewarded successfully' 
        });
    } catch (error) {
        console.error('Reward API Error:', error);
        return res.status(500).json({ 
            success: false, 
            message: 'Internal server error' 
        });
    }
});
module.exports = router;
