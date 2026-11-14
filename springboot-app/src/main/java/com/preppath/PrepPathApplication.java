
package com.preppath;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class PrepPathApplication {

    public static void main(String[] args) {
        SpringApplication.run(PrepPathApplication.class, args);
    }

    @GetMapping("/")
    public String home() {
        return "Welcome to PrepPath - Placement Preparation Tracker!";
    }
}
