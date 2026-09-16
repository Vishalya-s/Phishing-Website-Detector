import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;

public class Main {

    public static void main(String[] args) throws Exception {

        HttpServer server = HttpServer.create(
            new InetSocketAddress(8080),
            0
        );

        server.createContext(
            "/analyze",
            Main::analyzeWebsite
        );

        server.setExecutor(
            Executors.newCachedThreadPool()
        );

        server.start();

        System.out.println(
            "Java backend running on http://localhost:8080"
        );
    }


    private static void analyzeWebsite(
        HttpExchange exchange
    ) throws IOException {

        exchange.getResponseHeaders().add(
            "Access-Control-Allow-Origin",
            "*"
        );

        exchange.getResponseHeaders().add(
            "Content-Type",
            "application/json; charset=UTF-8"
        );


        String query =
            exchange.getRequestURI().getRawQuery();


        if (query == null || !query.startsWith("url=")) {

            sendResponse(
                exchange,
                "{\"error\":\"URL not provided\"}",
                400
            );

            return;
        }


        String encodedUrl =
            query.substring(4);


        String url =
            URLDecoder.decode(
                encodedUrl,
                StandardCharsets.UTF_8
            );


        System.out.println(
            "Received URL: " + url
        );


        try {

            /*
             * Instead of running:
             *
             * python predict.py URL
             *
             * we directly call:
             *
             * import predict
             * predict.predict(URL)
             *
             * This is the same method we already
             * confirmed works from PowerShell.
             */


            String pythonCode =
                "import predict, json, sys; " +
                "print(json.dumps(predict.predict(sys.argv[1])))";


            ProcessBuilder processBuilder =
                new ProcessBuilder(
                    "python",
                    "-c",
                    pythonCode,
                    url
                );


            processBuilder.directory(
                new File(
                    "C:/project-java/Phishing-Website-Detector/ml"
                )
            );


            processBuilder.redirectErrorStream(true);


            Process process =
                processBuilder.start();


            BufferedReader reader =
                new BufferedReader(
                    new InputStreamReader(
                        process.getInputStream(),
                        StandardCharsets.UTF_8
                    )
                );


            StringBuilder output =
                new StringBuilder();


            String line;


            while ((line = reader.readLine()) != null) {

                output.append(line);

            }


            int exitCode =
                process.waitFor();


            if (exitCode != 0) {

                System.out.println(
                    "Python error: " + output
                );

                sendResponse(
                    exchange,
                    "{\"error\":\"Python prediction failed\"}",
                    500
                );

                return;
            }


            String result =
                output.toString().trim();


            System.out.println(
                "ML Result: " + result
            );


            sendResponse(
                exchange,
                result,
                200
            );


        } catch (Exception e) {

            e.printStackTrace();


            sendResponse(
                exchange,
                "{\"error\":\"Unable to run ML model\"}",
                500
            );

        }

    }


    private static void sendResponse(
        HttpExchange exchange,
        String response,
        int statusCode
    ) throws IOException {


        byte[] responseBytes =
            response.getBytes(
                StandardCharsets.UTF_8
            );


        exchange.sendResponseHeaders(
            statusCode,
            responseBytes.length
        );


        OutputStream output =
            exchange.getResponseBody();


        output.write(responseBytes);


        output.close();

    }

}