![image](https://github.com/user-attachments/assets/5900500b-dd84-45c4-8bee-af18375256f5)


# An Alfred Workflow that uses your Ente Exports

Ente Auth CLI does [not support](https://github.com/ente-io/ente/discussions/716) exporting TOTP codes. To use this project, please export from the Ente app and then manually import them into the workflow's database using the `import` parameter.

> [!NOTE]
> In the future, the workflow will take care of the import.
> In addtion, once support for exporting codes via CLI is supported, we will use that instead.

## Setup

1. Install workflow from releases
2. Follow the instructions below to create the database

## Instructions

1. Open Alfred
2. Go to workflows
3. Right click the Ente 2FA workflow and press `Open In Finder`.
4. Export in plain text your Ente 2FA codes
5. Rename that file to secrets.txt and put it in the folder that got opened previously

![image](https://github.com/user-attachments/assets/d59a18a1-e63d-4206-9f87-fae9dbb11877)

It should look something like this
  
6. Open a Terminal and cd to the the folder containing the `main.py` file
7. Run `python main.py import secrets.txt`
8. Run `.ente` in Alfred and let the database populate

> [!WARNING]
> DELETE THE FILE AFTER THE IMPORT IS COMPLETE


> [!IMPORTANT]
> Changes made to the accounts in Ente Auth will not auto-update the database. Please rerun the steps.


## If you used to use momaek's Authy workflow

You already have a saved copy of the secrets on your machine, stored in your home directory named .authycache.json

```html
<!DOCTYPE html>
<html>
<head>
  <title>Convert Data</title>
</head>
<body>
  <script>
    let original_data = [
      {
        "name": "Microsoft: sopat712@sopat712.com",
        "original_name": "Microsoft:sopat712@sopat712.com",
        "digital": 6,
        "secret": "OA123JSDF123IBQ123BONOAN",
        "period": 0,
        "weight": 420
      },
      {
        "name": "Google: sopat712@sopat712.com",
        "original_name": "Google:sopat712@sopat712.com",
        "digital": 6,
        "secret": "IAVNAIV123867NAVI1NAV123123",
        "period": 0,
        "weight": 969
      }
    ];

    let convertedData = [];

    for (let item of original_data) {
      let newFormat = `otpauth://totp/${item.name}?secret=${item.secret}`;
      convertedData.push(newFormat);
    }

    console.log(convertedData.join("\n"));
  </script>
</body>
</html>
```

Paste this into your preferred text editor and replace what is between the original_data brackets with the data in your .authycache.json. Save the file as whatever.html. Then open the file with your browser. Copy paste the output into a new file and then import that into the Ente Auth app. Let me know if any issues pop up. I'll open up a discussion about it as well.

<a href="https://www.flaticon.com/free-icons/2fa" title="2fa icons">2fa icons created by Uniconlabs - Flaticon</a>
