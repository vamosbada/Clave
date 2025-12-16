package kr.ac.dankook.mobsys.bada.clave;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.POST;

public interface ClaveApiService {
    @POST("/api/analyze")
    Call<AnalyzeResponse> analyzeSentiment(@Body AnalyzeRequest request);
}
