package lab;

import io.restassured.RestAssured;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.empty;

class ApiSmokeTest {

    @BeforeAll
    static void setup() {
        RestAssured.baseURI = System.getProperty("baseUrl", "http://127.0.0.1:8000");
    }

    @Test
    void healthEndpointWorks() {
        given()
            .when()
            .get("/health")
            .then()
            .statusCode(200)
            .body("status", equalTo("ok"));
    }

    @Test
    void productsAreAvailable() {
        given()
            .when()
            .get("/api/products")
            .then()
            .statusCode(200)
            .body("items", not(empty()));
    }

    @Test
    void productDetailIsReturned() {
        given()
            .when()
            .get("/api/products/1")
            .then()
            .statusCode(200)
            .body("id", equalTo(1));
    }
}
