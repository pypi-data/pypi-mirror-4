# -*- coding: utf-8 -*-

class BaseFormatter(object):
    """
    Allows a model's instance to access an arbitrary class which extends BaseFormatter.
    This is usefull to separate instances methods that return structured data from instances 
    methods that return formatted data.
    The BaseFormatter class is some how a linking class between a view and a model. Methods of this
    class should return formatted data to be displayed for end-users, while instance methods from
    original model should only return structured data according to Python's good practices.
    Usage example.:
    on model:
        def ProductFormatter(BaseFormatter):
            def display_us_price(self):
                return "USD" + self.price
            def display_br_price(self):
                return "BRL" + self.price
    
        def Product(models.Model)
            name = models.CharField()
            price = models.DecimalField()
            ...
            formatter = ProductFormatter.new()
    
    on a view:
        product = Product.objects.get(pk=1)
        print product.formatter.display_br_price()
    """

    def __init__(self, instance):
        self.instance = instance

    def __getattr__(self, attr):
        try:
            return super(BaseFormatter, self).__getattr__(attr)
        except AttributeError:
            return getattr(self.instance, attr)

    @classmethod
    def new(cls):
        class FormatterDescriptor(object):
            def __get__(self, instance, owner):
                formatter = getattr(instance, 'formattercache', cls(instance))
                instance.formattercache = formatter
                return formatter
        return FormatterDescriptor()
