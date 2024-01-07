# To-Do List App with Keycloak Authentication and Stripe Payment

### To-do Flask webapp that uses keycloak for Authentication to let the user log in and add a to-do with title, description and time. All the API calls are handled by Graphql. There will be a option to buy a Pro license that will enable user to upload images in To-Do as well.

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
     ```
     ```bash
     docker run -d -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin -p 8080:8080 jboss/keycloak
     ```

5. **Keycloak Configuration:**
   - Visit `http://localhost:8080/auth` in a browser.
   - Log in with username = admin and password = admin.
   - Create a new realm named 'myapprealm'.
   - Set the Display name of your choice.
   - Click on the `Login` tab and ON `user registration` , `forgot password` , `login with email`
   - Create a new client with Client ID 'todolist' and set the root URL to `http://localhost:5000`.
   - Click on `keys` tab in the clients section and set the key and store passwords and click on `generate certificate`.
   - Copy the `certificate` which is the client secret key and add it to the `client_secrets.json` file.

   **NOTE:** If you change the name of the realm and client ID then you have to do the necessary changes in the `client_secrets.json` file.

6. **Run the App:**
   - In VSCode terminal, run the following commands:
    ```bash
     source flaskproj/Scripts/activate
    ```
    ```bash
     python app.py
    ```
   - If there's any error after running the above commands you can create a virtual environment and install the `requirements.txt`.


7. **Check the App:**
   - Visit `http://localhost:5000` to ensure the app is running successfully.
   - Click on 'register' when you see the Login page as we have not created any user earlier.

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
    - Access GraphQL API at `http://localhost:5000/graphql`.
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
