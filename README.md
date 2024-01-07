# Your App Name

## Steps to Start the App

1. **Code Editor:**
   - Make sure you have a code editor like VSCode installed.

2. **Docker Desktop:**
   - Install and set up Docker Desktop.

3. **Clone and Open in VSCode:**
   - Clone the repository and open it in your VSCode editor.

4. **Docker Keycloak Setup:**
   - Open Docker Desktop and keep it running in the background.
   - Open Git Bash terminal in VSCode and run the following commands:
     ```bash
     docker pull jboss/keycloak
     docker run -d -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin -p 8080:8080 jboss/keycloak
     ```

5. **Keycloak Configuration:**
   - Visit `localhost:8080/auth` in a browser.
   - Log in with username = admin and password = admin.
   - Create a new realm named 'myapprealm'.
   - Create a new client with Client ID 'todolist' and set the root URL to `localhost:5000`.
   - Generate the client secret key and add it to the `client_secrets.json` file.

6. **Run the App:**
   - In VSCode terminal, run the following command:
     ```bash
     python app.py
     ```

7. **Check the App:**
   - Visit `localhost:5000` to ensure the app is running successfully.

8. **Pro License Feature:**
   - Click on 'Update to Pro'.
   - Use the card details: 
     - Card: 4242424242424242
     - Expiry: any future date
     - CVV: any three numbers
     - Location: United States
     - Other fields: anything you want.

9. **Additional Payment Testing:**
   - For other payment-related testing, visit [Stripe Testing Cards](https://stripe.com/docs/testing#use-test-cards).

10. **GraphQL API:**
    - Access GraphQL API at `localhost:5000/graphql`.
    - Example GraphQL query:
      ```graphql
      query {
        user {
          id
          username
          email
          isPro
        }
        todos {
          title
          description
          timestamp
        }
      }
      ```
