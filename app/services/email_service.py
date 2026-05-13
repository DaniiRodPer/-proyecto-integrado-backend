import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv

load_dotenv()
BASE_URL_IP = os.getenv("BASE_URL_IP", "127.0.0.1")
PORT = os.getenv("PORT", "8000")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

"""
Función send_email_pin:
    params:
        recipient
        pin
        
Se conecta al servidor SMTP de Google y envía un email de recuperación de contraseña hecho con HTML
"""
def send_email_pin(recipient: str, pin: str):
    """Function to send the recovery email with Dovelia typography and embedded logo"""
    try:
        font_url = f"http://{BASE_URL_IP}:{PORT}/static/fonts/nyghtserif.ttf" 

        msg = MIMEMultipart('related')
        msg['From'] = f"Dovelia App <{EMAIL_SENDER}>"
        msg['To'] = recipient
        msg['Subject'] = "Tu código de recuperación de Dovelia"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="color-scheme" content="light dark">
                <meta name="supported-color-schemes" content="light dark">
                
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
                
                <style>
                    :root {{
                        color-scheme: light dark;
                        supported-color-schemes: light dark;
                    }}
                    
                    @font-face {{
                        font-family: 'NyghtSerif';
                        src: url('{font_url}') format('truetype');
                        font-weight: normal;
                        font-style: normal;
                    }}
                </style>
            </head>
            
            <body style="margin: 0; padding: 0; background-color: #231B18; background-image: linear-gradient(#231B18, #231B18); font-family: 'Montserrat', Arial, sans-serif;">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #231B18; background-image: linear-gradient(#231B18, #231B18); padding: 40px 20px;">
                    <tr>
                        <td align="center">
                            <table width="100%" max-width="500" border="0" cellspacing="0" cellpadding="0" 
                                   style="background-color: #160906; background-image: linear-gradient(#160906, #160906); border-radius: 28px; overflow: hidden; max-width: 500px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                                <tr>
                                    <td style="padding: 40px 30px; text-align: center;">
                                        
                                        <img src="cid:logo_app" alt="Dovelia Logo" width="120" style="margin-bottom: 10px;">
                                        
                                        <h1 style="color: #FFB5A7; -webkit-text-fill-color: #FFB5A7; font-family: 'NyghtSerif', Georgia, serif; font-size: 48px; margin: 0; font-weight: bold; font-style: italic;">
                                            Dovelia
                                        </h1>
                                        
                                        <div style="height: 2px; background-color: #2D2421; background-image: linear-gradient(#2D2421, #2D2421); margin: 20px auto; width: 50%;"></div>
                                        
                                        <h2 style="color: #FFFFFF; -webkit-text-fill-color: #FFFFFF; font-family: 'Montserrat', Arial, sans-serif; font-size: 20px; margin-top: 0; font-weight: 600; letter-spacing: 1px;">
                                            Restablecer contraseña
                                        </h2>
                                        
                                        <p style="color: #E6E1E0; -webkit-text-fill-color: #E6E1E0; font-family: 'Montserrat', Arial, sans-serif; font-size: 16px; line-height: 1.6; margin: 25px 0;">
                                            Hola,<br>
                                            Has solicitado restablecer tu contraseña. Utiliza el siguiente código PIN de seguridad dentro de la aplicación:
                                        </p>
                                        
                                        <div style="background-color: #120C0A; background-image: linear-gradient(#120C0A, #120C0A); border: 1px solid #FFB5A7; border-radius: 20px; 
                                                    padding: 25px; margin: 20px 0; display: inline-block; min-width: 180px;">
                                            <span style="font-family: 'Montserrat', Arial, sans-serif; font-size: 38px; font-weight: bold; letter-spacing: 10px; color: #FFB5A7; -webkit-text-fill-color: #FFB5A7; text-shadow: 0 0 10px rgba(255,181,167,0.3);">
                                                {pin}
                                            </span>
                                        </div>
                                        
                                        <p style="color: #ABA4A2; -webkit-text-fill-color: #ABA4A2; font-family: 'Montserrat', Arial, sans-serif; font-size: 13px; margin-top: 30px; font-style: italic;">
                                            Este código es de un solo uso. Si no has solicitado este cambio, puedes ignorar este correo.
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="background-color: #2D2421; background-image: linear-gradient(#2D2421, #2D2421); padding: 20px; text-align: center;">
                                        <p style="color: #FFB5A7; -webkit-text-fill-color: #FFB5A7; font-family: 'Montserrat', Arial, sans-serif; font-size: 11px; margin: 0; font-weight: bold; text-transform: uppercase; letter-spacing: 2px;">
                                            Dovelia &copy; 2026
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))

        try:
            with open("static/images/dovelia_logo.png", "rb") as img_file:
                logo_img = MIMEImage(img_file.read())
                logo_img.add_header('Content-ID', '<logo_app>')
                logo_img.add_header('Content-Disposition', 'inline')
                msg.attach(logo_img)
        except Exception as img_e:
            print(f"Aviso: No se pudo cargar el logo local. Comprueba la ruta. Error: {img_e}")

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Correo enviado con éxito a {recipient}")
    except Exception as e:
        print(f"Error enviando correo: {e}")