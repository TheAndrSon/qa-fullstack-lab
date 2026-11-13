package lab;

import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

import static org.junit.jupiter.api.Assertions.assertTrue;

@Disabled("Enable locally after installing Chrome and JDK 21")
class UiSmokeTest {

    @Test
    void homePageOpens() {
        WebDriver driver = new ChromeDriver();
        try {
            driver.get(System.getProperty("baseUrl", "http://127.0.0.1:8000"));
            assertTrue(driver.getTitle().contains("ShopSphere"));
        } finally {
            driver.quit();
        }
    }
}
