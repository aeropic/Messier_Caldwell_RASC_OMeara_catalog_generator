# Messier_Caldwell_RASC_O'Meara_catalog_generator
This is a python script to build a catalog of your Messier/Caldwell/RASC/O'Meara  objects astrophotographies

After the Messier, the Caldwell, the RASC catalogs, I needed to simplify all this and make a commun generic one : here it is including O'meara's "hidden treasures" and "secret deep" lists.
This project is a technical tool for observers. For detailed descriptions, history, and charts of the O'Meara objects, users are highly encouraged to purchase Stephen James O'Meara's books 'Hidden Treasures' and 'The Secret Deep' published by Cambridge University Press.

## important note: 
The script is written in Python, it then needs python to be installed on your machine.
If you use SIRIL, everything is already operationnal, you can skip next lines
If you don't use SIRIL : open and edit the .bat file to specify the path to your Python installation. Here, I pointed to SIRIL's path: 
:: Launch Python on the script located in the same folder: 
"C:\Program Files\Siril\python\python.exe" "Caldwell_generator.py"

## usage:
Simply organize your image files in a folder and add the string "M1, Mxx, C1, Cx or NGCxyz or ICabc" to the image names.
The script is able to manage files in .jpg, .jpeg, .png, .webp, .tif, .tiff and .lnk (window shortcut to image).

Place the "astro_catalog_generator.py" script and the "astro_catalog_launcher.bat" file in the same folder where the images are located. 
Double-click on "astro_catalog_launcher.bat", accept the Windows prompts, and it will automatically install missing python libraries (if any) and it generates an interactive HTML contact sheet. The .bat file, of course, only runs on PC...

If there are multiple objects in the same image, name the file with both objects (e.g.,NGC4038_NGC4039_antenna.jpg). 

<img width="1317" height="846" alt="cata" src="https://github.com/user-attachments/assets/b41ce7cf-49e7-4031-b952-cd606bdb0e34" />

thumbnails are created and stored into a "thumbnails" subfolder

NOTE : don't worry if you only see here screenshots in French, the english version is available (see at the end of this page)

## main functionalities

The script includes a mini-catalog, and the object type, for missing objects, is indicated in the middle of the thumbnail area. 
The thumbnails on the HTML page are clickable to access the zoomable image.
The marathon score is displayed at the top .
Placing the mouse over one object will display usefull data to prepare your imaging session inside a popup window (Tooltip) .
If you want to get more details, reference of each object (eg C42) is clickable and points to the corresponding telescopius page. For empty thumbnails, just click inside the thumbnail aera.

To switch between Messier/Caldwell/RASC/OMEARA catalogs just select the required catalog from the menu bar. There is also an option to select the "All in 1" catalog. In that case, the Messier objects are listed then Caldwell with no dupplication with the Messier, then the RASC with no dupplication with Messier/Caldwell and so on... All in 1 you get 504 objects to image, quite a good challenge !

you can also filter by type of objects (Nebula, galaxies, clusters and others)

<img width="1276" height="699" alt="nebu" src="https://github.com/user-attachments/assets/9d131ef7-6bf4-497f-b306-160a5f8fe396" />


In each catalog, and especially in the Caldwell and O'Meara, the name of some objects are painted in orange or red.
- orange means the object is always low on horizon (by default < 20°)
- red means, it will never be above your horizon
It should work for both North an South hemispheres !

The best season to observe each object is written in the thumbnail area. You may also want to filter each catalog by season just clicking of the season menu. (here summer-été is selected).
<img width="1210" height="659" alt="cata_summer" src="https://github.com/user-attachments/assets/a7deded7-636b-47e4-b196-d956e28ccd0c" />

There is also one menu to sort the objects by direction of the telescope according to your latitude. (My house is North/South with two terrasses one North one South !)
And the direction of observation is also displayed in the tooltip.
<img width="841" height="529" alt="cata_north" src="https://github.com/user-attachments/assets/88f843cc-cd34-45a6-be23-8399374cfd7a" />


To avoid being too disapointed when imaging a too small object, the tooltip displays the size of the object in orange when both dimensions are lower than than 2'

<img width="375" height="329" alt="smallsize" src="https://github.com/user-attachments/assets/faad9cbd-bcab-4bb8-8c8b-59e4eecda315" />

## tagging objects

When preparing some observations sessions, it may be usefull to tag the objects you want to image in priority. This can be done just with a right click on the thumbnail area. Right click will toggle ON/ON a small red heart and open a dialog box where you may want to deposit a small one-line comment. 

<img width="925" height="530" alt="hearts" src="https://github.com/user-attachments/assets/657b395e-63ad-4ba1-a829-60ee41e2219d" />


<img width="1122" height="552" alt="cata_comment" src="https://github.com/user-attachments/assets/10b20871-843f-4763-b36f-cb6ac17e1164" />

Once done, the note will appear in tooltip
<img width="1029" height="681" alt="cata_note" src="https://github.com/user-attachments/assets/f060caad-9947-4c6c-a1c6-cc2f80ee3ebd" />

In addition, to increase visibility, objects tagged and with a note will appear with a filled heart while objects tagged but without note will be displayed with a hollow heart.

<img width="458" height="307" alt="cata_hollow_heart" src="https://github.com/user-attachments/assets/fc3e8556-d3f7-4038-8d8b-669e651be1f4" />


### the TODO.txt file 

As the browsers have a cache where is stored persistent data, the list of your favorite objects including the notes is persistent as long as you do not change your browser and you do not empty the cache. But there is a way to permanently store this list inside a TODO.txt file. When clicking on the upper right icon with a floppy disk, the file is created and stored into your browser "uploads" diectory. You have to drag and drop this file into the image and script folder to get it recognized at next startup. The file can be manually edited to add/remove hearts and comments (be carefull with the syntax) !
here is an example:

<img width="364" height="419" alt="cata_edit_todo" src="https://github.com/user-attachments/assets/0a6e51e5-3213-4535-9dcf-d157e777139e" />

## smart Tooltip and  visible objects of the day

Since version V5.1, in the tooltip there is a plot of object altitude curve for the coming night. The curve is painted in yellow for South objects and blue for North ones.
The horizontal dot green line is at 30°.
The curve is centered on the night duration. Progessive light blue to black background are the dates of sunset, successive penumbras, then dark night, successive penumbras, sunrise up to day light blue again.

<img width="559" height="556" alt="cata_tooltip_curve" src="https://github.com/user-attachments/assets/ee37bd8d-25b6-4c2e-8270-2956f4848770" />

Should you want to get more information on the times and altitude values, just move the mouse on the name area and right click. 

<img width="531" height="511" alt="cata_rightclick" src="https://github.com/user-attachments/assets/6083c6b9-5977-41ae-8609-abd9a06cf8d6" />

The tooltip position will be frozen, the frame is painted in red. Now move the mouse inside the curve area and you get local-time/alt displayed. 

<img width="365" height="345" alt="cata_tooltip2" src="https://github.com/user-attachments/assets/48175d2e-0960-4235-a4c0-8f111296c269" />

To exit, right click anywhere in the tooltip.

From V5.1 you can also filter the objects to display only the tonight visible objects (according to your latitude, timezone and horizon line)

<img width="620" height="312" alt="tonight" src="https://github.com/user-attachments/assets/f2ec1dd3-b8d3-43bb-bb2f-14e2d4a7b438" />

## search tool

At the top left of the screen there is a "question mark" button, press it and you'll be invited to type an object reference

<img width="870" height="213" alt="cata_question" src="https://github.com/user-attachments/assets/03ea4ba4-60b6-4575-b611-4bf4a5b7a7f2" />

Once OK is pressed, if the object is found in any catalog (first found object will win !), the catalog in which the object is located will be selected and the page will scroll to the object. A green "jacky tuning style" frame will be displayed to catch your eyes !

<img width="666" height="686" alt="cata_found" src="https://github.com/user-attachments/assets/7c8ca460-1511-42ab-be9d-baaa39378e0e" />



## editing the python file
you can also edit the python file and change this value
-    "LIMIT_SMALL_OBJECT": 120                     # arcseconds ; paint small objects size in orange

you can edit the python file and change those lines according to your location :
-   "LATITUDE": 43.6,                             # your latitude
-   "LIMIT_IMPOSSIBLE": 0,                          # degrees : change here if your horizon is masked
-   "LIMIT_DIFFICILE": 20

## translation in english or other language
You can easily translate the script in any langage as all strings are gathered in a separate file named "LANG_database.py". Place this file in the same directory as the script and all screens will be in english, remove this file and the default French language will be used.

<img width="946" height="543" alt="cata_EN" src="https://github.com/user-attachments/assets/702b9627-89ba-4004-b558-17dc720d626c" />

Spanish language is ready also. 
(ES_LANG_database.py) rename the file without "ES_".

For other languages, just translate the strings into your language, save the file as "LANG_database.py". If you're lazy, ask Gemini AI to do this job for you ...
(Should you do this, I would appreciate if you could provide me with the translated file)

## bottom line 
Let me know if it works for you too and if you see any improvements we could make!





