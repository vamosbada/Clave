package kr.ac.dankook.mobsys.bada.clave;

import com.google.gson.annotations.SerializedName;

public class AnalyzeResponse {
    @SerializedName("sentiment")
    private String sentiment;

    @SerializedName("confidence")
    private double confidence;

    @SerializedName("analysis")
    private Analysis analysis;

    @SerializedName("consistency_info")
    private ConsistencyInfo consistencyInfo;

    public String getSentiment() {
        return sentiment;
    }

    public double getConfidence() {
        return confidence;
    }

    public Analysis getAnalysis() {
        return analysis;
    }

    public ConsistencyInfo getConsistencyInfo() {
        return consistencyInfo;
    }

    public static class Analysis {
        @SerializedName("analysis_focus")
        private String analysisFocus;

        @SerializedName("cultural_context")
        private String culturalContext;

        @SerializedName("key_expression")
        private String keyExpression;

        @SerializedName("translation")
        private String translation;

        public String getAnalysisFocus() {
            return analysisFocus;
        }

        public String getCulturalContext() {
            return culturalContext;
        }

        public String getKeyExpression() {
            return keyExpression;
        }

        public String getTranslation() {
            return translation;
        }
    }

    public static class ConsistencyInfo {
        @SerializedName("num_calls")
        private int numCalls;

        @SerializedName("agreement")
        private String agreement;

        public int getNumCalls() {
            return numCalls;
        }

        public String getAgreement() {
            return agreement;
        }
    }
}
