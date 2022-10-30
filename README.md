# vCard-photo
Add a photo to vCard V3.0

This project adds a photo/avatar to each contact in your ***.vcf** file in case it don't have; it saves your new ***.vcf** in ***_photos.vcf**.

My contact-software doesn't support vCard 4.0 (Shame on Infomaniak for this point but they have other advantages ;-))
So this project brutforce the switch to vCard 3.0 (Sorry ... I'm really sorry). 

Avatars are generated via https://avatars.dicebear.com
You can choose your style by editing DICEBEAR_SPRITES dictionnary. If you choose different styles, project will randomly choose one of them. 
Colored background is automaticaly added. Project uses a hash to determine the RGB-color, based on the first name of your contact.

No test for the moment (I have to learn how to write it).

To Do :
- Add all documentation to defined function
- Add possibility to choose your background color

What I will not implement :
- support of vCard 4.0 (Sorry guys !)
