from zope import component
from Products.Five.browser import BrowserView


class SampleView(BrowserView):
    """Sample view is used as base view to manage some needed
    information like the site url"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        self.portal_state = component.getMultiAdapter((self.context, self.request),
                                                      name="plone_portal_state")
        self.portal_url = self.portal_state.portal_url()
        self.sample_url = '%s/++resources++collective.js.ckeditor/samples' % self.portal_url


class SamplePostedData(SampleView):
    
    def update(self):
        """from PHP posteddata.php file to Plone:
        <?php
        if ( isset( $_POST ) )
            $postArray = &$_POST ;            // 4.1.0 or later, use $_POST
        else
            $postArray = &$HTTP_POST_VARS ;    // prior to 4.1.0, use HTTP_POST_VARS
        
        foreach ( $postArray as $sForm => $value )
        {
            if ( get_magic_quotes_gpc() )
                $postedValue = htmlspecialchars( stripslashes( $value ) ) ;
            else
                $postedValue = htmlspecialchars( $value ) ;
        
        ?>
                <tr>
                    <th style="vertical-align: top"><?php echo $sForm?></th>
                    <td><pre class="samples"><?php echo $postedValue?></pre></td>
                </tr>
            <?php
        }
        ?>
        """
        super(SamplePostedData, self).update()
        form = self.request.form
        self.values = []  # {'postedValue':  value, 'sForm': key}
        for key in form:
            self.values.append({'sForm': key, 'postedValue': form[key]})
