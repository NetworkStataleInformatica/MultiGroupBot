<div align="center">
    <h2>Multi Group Bot</h2>
	<img src="0.png">
	<br>
	<br>
	<hr>
	<p>
		<p>
			<sup>
         <b>Project under development</b><br><br>
			</sup>
		</p>
	</p>
    <p>
</div>
Andrea, [23.04.20 14:03]
Come ho detto prima a lui, scusate ma non ho davvero tempo

Avevo solo fatto una bozza taaanto tempo fa, ma non ho nemmeno piú il codice (non l'avevo neanche caricato online).


L'idea é di avere un bot simile a @grouphelpbot (quello di tarallo prima e pighizzini poi), o meglio un bot con un subset delle sue funzioni, cioé quelle che usiamo noi. In particolare ci servono sicuramente comandi per fare un annuncio, ban/warn/mute, creare comandi personalizzati.

La limitazione del grouphelp é che é pensato per gestire un singolo gruppo, non un insieme di gruppi. Vuol dire che se vuoi comunicare qualcosa sui gruppi principali (non degli insegnamenti), devi scrivere lo stesso messaggio 3 volte. Se entra un tizio ed é un palese troll, lo vuoi bannare una volta da tutto il network, non perdere 10 minuti a farlo manualmente da tipo 20+ gruppi diversi.

La mia idea idea é, quindi, avere una cosa tipo

/warn [where], dove nello specifico

/warn => aggiunge un warn globale. Se raggiunge il limite (normalmente 3, ma si puó modificare), viene bannato ovunque

/warn -in PRINCIPALI => warna in tutti i gruppi principali 

/warn -in PRIMO_ANNO => warna in tutti i gruppi del primo anno

/warn -in THIS => warna solo nel gruppo corrente 


Naturalmente, PRINCIPALI e PRIMO_ANNO sono esempi, non vanno hard-codati, ma ci vuole un comando da amministratore per creare degli insiemi/label. 





L'idea, direi, é che il bot vada aggiunto a ogni singolo gruppo. Internamente, appena entrato registra l'id di quel gruppo e lo aggiunge all'insieme ALL (un bot appena entra conosce l'id della chat/gruppo). 
Poi hai un dizionario di insiemi, cioé un dict[String, Set(String)]. Es insiemi['PRIMO_ANNO'] = { "[id_continuo]", "[id_gruppo_matricole]" ....... }

Quando esegui un comando, fai un foreach sul set che prendi dal dizionario, ed esegui il comando su ogni gruppo, controllando che l'utente sia in quel gruppo

Non ricordo se si puó pre-bannare un utente, ma in caso contrario bisogna salvarsi anche un set di utenti limitati (non serve di tutti) e, ogni volta che qualcuno entra in un gruppo, controllare se il suo id é in questo set di bannati. Se si, lo banni subito anche dal gruppo nuovo (se banno un troll in continuo, e lui era solo li, non voglio preoccuparmi di bannarlo a mano da gruppi nei quali entra dopo)

Andrea, [23.04.20 14:04]
Questa cosa dell'applicare i comandi su "insiemi" di gruppi non é utile solo per la moderazione in senso stretto (ban/warn/mute) ma anche per annunci e comandi. Es. se vuoi fare un comando carino per il drive lo fai una volta e lo applichi a tutti i gruppi principali subito. Se lo modifichi, applichi la modifica ovunque

Andrea, [23.04.20 14:08]
L'elenco dei gruppi ecc. va salvato da qualche parte. Finché usi il bot in maniera privata va bene anche una semplice serializzazione (trasformi le liste in json, per dire), se vuoi renderlo pubblico hai bisogno di 

1) Un sistema di autenticazione o clonazione (tipo quello di grouphelp) 
2) Un modo per tenere i dati di tutti

Andrea, [23.04.20 14:09]
un posto dove tenere i dati ti serve comunque, che tu ci metta il db o meno

Andrea, [23.04.20 14:10]
Anche se salvi tutto in json, lo devi salvare da qualche parte. Altrimenti appena riavvii il bot (e lo farai spesso, perché all'inizio ti si impalla, e lo usi in locale), perdi i dati