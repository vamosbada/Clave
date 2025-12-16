package kr.ac.dankook.mobsys.bada.clave;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.button.MaterialButton;
import com.google.android.material.chip.Chip;
import com.google.android.material.textfield.TextInputEditText;

public class MainActivity extends AppCompatActivity {

    private TextInputEditText editTextInput;
    private MaterialButton btnAnalyze;
    private ProgressBar progressBar;
    private Chip chipPositive, chipNegative, chipNeutral;

    // 예시 문장
    private static final String EXAMPLE_POSITIVE = "Ayer fue amazing, la pasé super bien con mis amigos y we had so much fun!";
    private static final String EXAMPLE_NEGATIVE = "Estoy so tired of this, siempre the same problems y nadie helps me.";
    private static final String EXAMPLE_NEUTRAL = "I need to go al supermercado porque no hay milk en la casa.";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // UI 요소 초기화
        initViews();

        // 버튼 클릭 리스너
        btnAnalyze.setOnClickListener(v -> analyzeSentiment());

        // 예시 칩 클릭 리스너
        chipPositive.setOnClickListener(v -> editTextInput.setText(EXAMPLE_POSITIVE));
        chipNegative.setOnClickListener(v -> editTextInput.setText(EXAMPLE_NEGATIVE));
        chipNeutral.setOnClickListener(v -> editTextInput.setText(EXAMPLE_NEUTRAL));
    }

    private void initViews() {
        editTextInput = findViewById(R.id.editTextInput);
        btnAnalyze = findViewById(R.id.btnAnalyze);
        progressBar = findViewById(R.id.progressBar);
        chipPositive = findViewById(R.id.chipPositive);
        chipNegative = findViewById(R.id.chipNegative);
        chipNeutral = findViewById(R.id.chipNeutral);
    }

    private void analyzeSentiment() {
        String text = editTextInput.getText().toString().trim();

        // 입력 검증
        if (text.isEmpty()) {
            Toast.makeText(this, "텍스트를 입력해주세요", Toast.LENGTH_SHORT).show();
            return;
        }

        if (text.length() > 100) {
            Toast.makeText(this, "100자 이내로 입력해주세요", Toast.LENGTH_SHORT).show();
            return;
        }

        // 로딩 시작
        showLoading(true);

        // API 호출
        AnalyzeRequest request = new AnalyzeRequest(text);
        ClaveApiService apiService = RetrofitClient.getApiService();

        apiService.analyzeSentiment(request).enqueue(new retrofit2.Callback<AnalyzeResponse>() {
            @Override
            public void onResponse(retrofit2.Call<AnalyzeResponse> call, retrofit2.Response<AnalyzeResponse> response) {
                showLoading(false);

                if (response.isSuccessful() && response.body() != null) {
                    AnalyzeResponse result = response.body();

                    // ResultActivity로 이동
                    Intent intent = new Intent(MainActivity.this, ResultActivity.class);
                    intent.putExtra("input_text", text);
                    intent.putExtra("sentiment", result.getSentiment());
                    intent.putExtra("confidence", result.getConfidence());
                    intent.putExtra("analysis_focus", result.getAnalysis().getAnalysisFocus());
                    intent.putExtra("cultural_context", result.getAnalysis().getCulturalContext());
                    intent.putExtra("key_expression", result.getAnalysis().getKeyExpression());
                    intent.putExtra("translation", result.getAnalysis().getTranslation());
                    intent.putExtra("agreement", result.getConsistencyInfo().getAgreement());
                    startActivity(intent);
                } else {
                    Toast.makeText(MainActivity.this, "분석 실패: " + response.code(), Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(retrofit2.Call<AnalyzeResponse> call, Throwable t) {
                showLoading(false);
                Toast.makeText(MainActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    private void showLoading(boolean show) {
        if (show) {
            progressBar.setVisibility(View.VISIBLE);
            btnAnalyze.setEnabled(false);
        } else {
            progressBar.setVisibility(View.GONE);
            btnAnalyze.setEnabled(true);
        }
    }
}
