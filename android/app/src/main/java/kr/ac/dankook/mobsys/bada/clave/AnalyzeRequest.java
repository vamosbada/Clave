package kr.ac.dankook.mobsys.bada.clave;

public class AnalyzeRequest {
    private String text;

    public AnalyzeRequest(String text) {
        this.text = text;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }
}
