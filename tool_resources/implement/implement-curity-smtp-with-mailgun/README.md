# Implement Curity SMTP with Mailgun

This directory contains the configuration needed to re-enable SMTP with Mailgun in the Curity Identity Server.

## Files

- `smtp-config.xml`: Contains the email provider configuration block.

## Integration Instructions

To re-enable SMTP, you need to modify the Curity `config.xml` file and potentially `polytope.yml`.

1.  **Add Email Provider Definition**:
    Copy the contents of `smtp-config.xml` and paste it inside the `<facilities>` element in `config.xml`. If an `<email-providers>` element already exists, merge the `<email-provider>` into it.

    ```xml
    <facilities xmlns="https://curity.se/ns/conf/base">
      <!-- ... other facilities ... -->
      <email-providers>
        <email-provider>
          <id>default-email-provider</id>
          <smtp>
            <smtp-host>smtp.eu.mailgun.org</smtp-host>
            <smtp-port>587</smtp-port>
            <default-sender>accounts@bluetext.dev</default-sender>
            <username>accounts@bluetext.dev</username>
            <password>YOUR_PASSWORD</password>
          </smtp>
        </email-provider>
      </email-providers>
      <!-- ... -->
    </facilities>
    ```

    *Note: The password in `smtp-config.xml` is hardcoded. If you prefer to use environment variables, you can use `${MAILGUN_SMTP_PASSWORD}` syntax if Curity is configured to support it, or inject it via startup scripts.*

2.  **Configure Zone**:
    Add the email provider to your zone configuration (usually under `<environments><environment><services><zones><default-zone>`).

    ```xml
    <zones>
      <default-zone>
        <email-provider>default-email-provider</email-provider>
        <!-- ... other zone settings ... -->
      </default-zone>
    </zones>
    ```

3.  **Configure Authenticators**:
    Add the email provider to any authenticators that require email functionality (e.g., HTML Form authenticator).

    ```xml
    <authenticators>
      <authenticator>
        <id>default-authenticator</id>
        <html-form xmlns="https://curity.se/ns/conf/authenticators/html-form">
          <!-- ... other settings ... -->
          <email-provider>default-email-provider</email-provider>
        </html-form>
      </authenticator>
    </authenticators>
    ```

4.  **Restore Environment Variables (Optional)**:
    If you wish to pass SMTP credentials via environment variables, you may need to add them back to `polytope.yml`:

    ```yaml
            - { name: MAILGUN_SMTP_USERNAME, value: pt.secret mailgun-smtp-username }
            - { name: MAILGUN_SMTP_PASSWORD, value: pt.secret mailgun-smtp-password }