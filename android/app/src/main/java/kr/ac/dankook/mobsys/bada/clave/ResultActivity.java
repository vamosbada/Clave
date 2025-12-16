package kr.ac.dankook.mobsys.bada.clave;

import android.graphics.Color;
import android.os.Bundle;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.card.MaterialCardView;
import com.google.android.material.chip.Chip;

public class ResultActivity extends AppCompatActivity {

    private TextView textInputDisplay, textSentiment, textConfidence, textAgreement;
    private TextView textAnalysisFocus, textCulturalContext, textTranslation;
    private TextView chipKeyExpression;
    private ProgressBar progressConfidence;
    private MaterialCardView cardSentiment;
    private MaterialToolbar toolbar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_result);

        initViews();
        displayResults();
    }

    private void initViews() {
        toolbar = findViewById(R.id.toolbar);
        textInputDisplay = findViewById(R.id.textInputDisplay);
        textSentiment = findViewById(R.id.textSentiment);
        textConfidence = findViewById(R.id.textConfidence);
        textAgreement = findViewById(R.id.textAgreement);
        textAnalysisFocus = findViewById(R.id.textAnalysisFocus);
        textCulturalContext = findViewById(R.id.textCulturalContext);
        textTranslation = findViewById(R.id.textTranslation);
        chipKeyExpression = findViewById(R.id.chipKeyExpression);
        progressConfidence = findViewById(R.id.progressConfidence);
        cardSentiment = findViewById(R.id.cardSentiment);

        // 뒤로가기 버튼
        toolbar.setNavigationOnClickListener(v -> finish());
    }

    private void displayResults() {
        // Intent로부터 데이터 받기
        String inputText = getIntent().getStringExtra("input_text");
        String sentiment = getIntent().getStringExtra("sentiment");
        double confidence = getIntent().getDoubleExtra("confidence", 0.0);
        String analysisFocus = getIntent().getStringExtra("analysis_focus");
        String culturalContext = getIntent().getStringExtra("cultural_context");
        String keyExpression = getIntent().getStringExtra("key_expression");
        String translation = getIntent().getStringExtra("translation");
        String agreement = getIntent().getStringExtra("agreement");

        // 입력 텍스트 표시
        textInputDisplay.setText(inputText);

        // 번역 표시
        textTranslation.setText(translation != null ? translation : "번역 정보 없음");

        // 감성 결과 표시
        String emoji = getSentimentEmoji(sentiment);
        String sentimentText = getSentimentText(sentiment);
        textSentiment.setText(emoji + " " + sentimentText);

        // 카드 배경색 설정
        int cardColor = getSentimentColor(sentiment);
        cardSentiment.setCardBackgroundColor(cardColor);

        // 신뢰도 표시
        int confidencePercent = (int) (confidence * 100);
        textConfidence.setText(confidencePercent + "%");
        progressConfidence.setProgress(confidencePercent);

        // 일치도 표시
        textAgreement.setText("일치도: " + agreement + " ✓");

        // 핵심 표현
        chipKeyExpression.setText(keyExpression);

        // 분석 상세
        textAnalysisFocus.setText(analysisFocus);
        textCulturalContext.setText(culturalContext);
    }

    private String getSentimentEmoji(String sentiment) {
        switch (sentiment.toLowerCase()) {
            case "positive":
                return "😊";
            case "negative":
                return "😔";
            case "neutral":
            default:
                return "😐";
        }
    }

    private String getSentimentText(String sentiment) {
        switch (sentiment.toLowerCase()) {
            case "positive":
                return "Positive";
            case "negative":
                return "Negative";
            case "neutral":
            default:
                return "Neutral";
        }
    }

    private int getSentimentColor(String sentiment) {
        switch (sentiment.toLowerCase()) {
            case "positive":
                return Color.parseColor("#E3F2FD"); // 파스텔 블루 배경
            case "negative":
                return Color.parseColor("#FFE8E8"); // 파스텔 코랄 배경
            case "neutral":
            default:
                return Color.parseColor("#F5F5F5"); // 파스텔 그레이 배경
        }
    }
}
