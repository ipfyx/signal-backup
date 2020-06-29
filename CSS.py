HEAD = """
  <!DOCTYPE html>
  <html>
    <head>
      <meta charset='utf-8'>
      <link href="bootstrap-4.4.1-dist/css/bootstrap.css" rel="stylesheet">
      <link href="signal.css" rel="stylesheet">
    </head>
    <body>
  """

NAVBAR = """
    <div class="container">
  
      <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="#">Navbar</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      </nav>
  """

FOOTER = """
    </body>
  </html>
  """


SMS_CSS = """
        <section class="row">
          <div class="col-md-6 msg_{css} {offset}">
          <div class="col-md-12 name_{css}">
            {contact_name} - {date}
          </div>
          {msg}
          {reaction}
          </div>
        </section>
  """

MMS_IMG = """
      <section class="row">
        <div class="col-md-6 msg_{css} {offset}">
        <div class="col-md-12 name_{css}">
          {contact_name} - {date}
        </div>
          <a href="{filename}">
          <img src="{filename}">
          </a>
        {msg}
        {reaction}
        </div>
      </section>
  """

MMS_QUOTE = """
      <section class="row">
        <div class="col-md-6 msg_{css} {offset}">
        <div class="col-md-12 name_{css}">
        {contact_name} - {date}
        </div>
        <div class="col-md-12 name_{css}">
	{contact_quoted} - {quote_date}
        <div class="col-md-12 quote_{css}">
        {quote}
        </div>
        </div>
	{msg}
        {reaction}
        </div>
      </section>
  """
MMS_QUOTE_IMG = """
      <section class="row">
        <div class="col-md-6 msg_{css} {offset}">
        <div class="col-md-12 name_{css}">
        {contact_name} - {date}
        </div>
        <div class="col-md-12 name_{css}">
        {contact_quoted} - {quote_date}
        <div class="col-md-12 quote_{css}">
        <a href="{filename}">
          <img src="{filename}">
        </a>
        {quote}
        </div>
        </div>
	{msg}
        {reaction}
        </div>
      </section>
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
          <a href="{filename}">
            <img src="{filename}">
          </a>
"""

QUOTE = """
        <div class="col-md-12 name_{css}">
        {contact_quoted} - {quote_date}
	  <!-- Quoted msg and file -->
          <div class="col-md-12 quote_{css}">
	  {filename}
          {quote}
          </div>
        </div>
"""
