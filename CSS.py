HEAD = """
  <!DOCTYPE html>
  <html>
    <head>
      <meta charset='utf-8'>
      <link href="bootstrap/css/bootstrap.css" rel="stylesheet">
      <link href="bootstrap/css/signal.css" rel="stylesheet">
    </head>
    <body>
  """

NAVBAR = """
    <div class="container">
  
      <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="index.html">INDEX</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      </nav>
  """

FOOTER = """
    </body>
  </html>
  """

IDEA = """
      <section class="row">
        <div class="col-md-6 msg_{css} {offset}">

	<!-- Writer and date sent -->
        <div class="col-md-12 name_{css}">
        {contact_name} - {date}
        </div>

	<!-- Quoted contact and date sent -->
        <div class="col-md-12 name_{css}">
        {contact_quoted} - {quote_date}

	<!-- Quoted msg and file -->
        <div class="col-md-12 quote_{css}">
        <a href="{filename}">
          <img src="{filename}">
        </a>
        {quote}
        </div>

	<!-- Msg filename -->
	</div>
          <a href="{filename}">
            <img src="{filename}">
          </a>
        </div>

	<!-- Msg -->
	{msg}

	<!-- Reaction -->
        {reaction}
        </div>

      </section>
  """

TEMPLATE = """
      <section class="row">
        <div class="col-md-6 msg_{css} {offset}">

	<!-- Writer and date sent -->
        <div class="col-md-12 name_{css}">
        {contact_name} - {date}
        </div>

	<!-- Quoted contact and date sent -->
        {quoted_msg} 

	<!-- Msg filename -->
	{filename_sent}	

	<!-- Msg -->
	{msg_sent}

	<!-- Reaction -->
        {reactions}
        </div>

      </section>
  """

REACTION_CSS = """
          <div class="col-md-2 react_{css} offset-md-10">
          {reactions}
          </div>
  """

# Msg filename
FILENAME ="""
          <p>
          <a href="{filename}">
            <img src="{filename}">
          </a>
          </p>
"""

VIDEO ="""
          <p>
          <a href="{filename}">{filename}</a>
          <video width="540" controls <source src="{filename}" type="{type}"></video>
          </p>
"""

PDF ="""
          <p>
          <a href="{filename}">
            <embed src="{filename}" width=540/>
          </a>
          </p>
"""


QUOTE = """
        <div class="col-md-12 name_{css}">
        {contact_quoted} - {quote_date}
	  <!-- Quoted msg and file -->
          <div class="col-md-12 quote_{css}">
	  {quote_filename}
          {quote}
          </div>
        </div>
"""

TOTAL = """
      <section class="row">
        <div class="col-md-6 msg_myself">
          <p>
            sent : {total_sent}
          </p>
          <p>
            recieved : {total_recv}
          </p>
      </section>
  """


INDEX = """
      <section class="row">
        <div class="col-md-6 msg_myself">
          <p>
            <a href="{link}.html">{link}</a>
          </p>
          <p>
            Sent by {sender} : {msg_sent} messages <br>
            Sent by {reciever} : {msg_recv} messages
          </p>
      </section>
  """


