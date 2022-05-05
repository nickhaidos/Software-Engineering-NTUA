# TL21-09

Semester project for class "Software Engineering 2021-2022" (7th semester ECE NTUA)

Εξαμηνιαία Εργασία στο μάθημα "Τεχνολογία Λογισμικού" 2021-2022

Μέλη Ομάδας:
- Χάιδος Νικόλαος, 03118096
- Χάιδος Παναγιώτης, 03118862

Για την σχεδίαση της εφαρμογής μας χρησιμοποιήσαμε τα εξής εργαλεία:
- Python(Flask), για το Back-End και το API
- MySQL(MariaDB), για το DBMS
- Visual Paradigm, για τα διαγράμματα
- Postman (+Newman) για το Testing/Documentation


Όσο για το στήσιμο της εφαρμογής, χρειάζεται να κάνουμε τα εξής βήματα:
1. Να φορτώσουμε το αρχείο dump.sql σε ένα DBMS που υποστηρίζει MySQL (προτιμότερα το MariaDB, αφού αυτό χρησιμοποιήθηκε για την ανάπτυξη της εφαρμογής)
2. Να κατεβάσουμε τις εξής βιβλιοθήκες της Python: Flask, Flask-mysqldb, Pandas  (μαζί με όλα τα requirements της καθεμιάς που γίνονται install αυτόματα)
3. Τέλος, πρέπει να σιγουρευτούμε ότι το DBMS έχει ενεργοποιήσει την βάση δεδομένων στο Port 3306

Ύστερα, τρέχοντας το αρχείο app.py, μπορούμε να χρησιμοποιήσουμε τα Endpoints του API, με baseURL το "http://localhost:9103/interoperability/api/"
