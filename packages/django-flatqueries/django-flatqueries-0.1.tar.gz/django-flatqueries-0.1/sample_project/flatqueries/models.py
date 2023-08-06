from django.db import connection, models

MAX_QUERY_TITLE = 50

class Query(models.Model):
    title = models.CharField(blank=False, null=False, max_length=MAX_QUERY_TITLE,
        help_text='Short, simple, easy-to-remember title')
    description = models.TextField(blank=True, null=True)
    sql = models.TextField(blank=False, null=False)

    @models.permalink
    def get_absolute_url(self):
        return ('flatqueries.views.run', (), { 'id': str(self.id) })
     
    def run(self):   
        """
        Executes sql and returns a tuple of (headers, rows), where:
        - headers = list of column names
        - rows = list of rows, where each row is a list of column values
        """
        cursor = connection.cursor()
        cursor.execute(self.sql)
        headers = [ desc[0] for desc in cursor.description ]
        rows = cursor.fetchall()
        return (headers, rows)
        
    class Meta:
        verbose_name = 'flat query'
        verbose_name_plural = 'flat queries'
        permissions = (
            ('can_run_query', 'Can run query'),
        )

