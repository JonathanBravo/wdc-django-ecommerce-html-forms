from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound

from products.models import Product, Category, ProductImage


def products(request):
    #Get all products from the DB using the Product model
    products = Product.objects.all()

    # Get up to 4 `featured=true` Products to be displayed on top
    featured_products = products.filter(featured=True)
    if featured_products.count()>4:
        featured_products = featured_products[:4]

    return render(
        request,
        'products.html',
        context={'products': products, 'featured_products': featured_products}
    )


def create_product(request):
    #Get all categories from the DB
    categories = Category.objects.all()
    
    if request.method == 'GET':
        # Render 'create_product.html' template sending categories as context
        return render(
            request, 
            'create_product.html',
            context={'categories': categories}
            
        )  
    elif request.method == 'POST':
        # Validate that all fields below are given in request.POST dictionary,
        # and that they don't have empty values.

        # If any errors, build an errors dictionary with the following format
        #and render 'create_product.html' sending errors and categories as context

        # errors = {'name': 'This field is required.'}
        fields = ['name', 'sku', 'price']
        errors = {}
        
        for field in fields:
            if not request.POST[field]:
                errors[field] = 'This field is required.'
                
        # If no errors so far, validate each field one by one and use the same
        # errors dictionary created above in case that any validation fails
        if not errors:
            if len(request.POST['name'])>100:
                errors['name'] = "Name can't be more than 100 chars"
            if len(request.POST['description'])>1000:
                errors['description'] = "Description can't be more than 1000 chars"
            if float(request.POST['price']) > 10000.00 or float(request.POST['price'])<0:
                errors['price'] = "Price can't be greater than 10k"
            if len(request.POST['sku'])>8:
                errors['sku']= "SKU can't be more than 8 chars"


        #if any errors so far, render 'create_product.html' sending errors and
        # categories as context
        # <YOUR CODE HERE>
        if errors:
            return render(
                request,
                'create_product.html',
                context={'errors': errors, 'categories': categories}
            )
        

        # If execution reaches this point, there aren't any errors.
        # Get category from DB based on category name given in payload.
        # Create product with data given in payload and proper category
        category = Category.objects.get(name=request.POST['category'])
        name = request.POST['name']
        description = request.POST['description']
        price = float(request.POST['price'])
        sku = request.POST['sku']
   
    
        product_created, created = Product.objects.get_or_create(
            category = category,
            name = name,
            sku = sku,
            price = price,
            description = description,
            featured = True
            )
        if not created:
            errors['duplicate'] = 'Cannot have duplicate items'
            return render(
                request,
                'create_product.html',
                context={'errors': errors, 'categories': categories}
            )
        #Up to three images URLs can come in payload with keys 'image-1', 'image-2', etc.
        # For each one, create a ProductImage object with proper URL and product
        # <YOUR CODE HERE>
        pics = ['image_1','image_2','image_3']
        for pic in pics:
            if request.POST.get(pic):
                ProductImage.objects.create(
                    url = request.POST[pic],
                    product = product_created
                    )

        # Redirect to 'products' view
        return redirect('products')


def edit_product(request, product_id):
    #Get product with given product_id
    product = Product.objects.get(id=product_id)
    pic_urls = product.productimage_set.all()
    # Get all categories from the DB
    categories = Category.objects.all()
    
    if request.method == 'GET':
        # Render 'edit_product.html' template sending product, categories and
        #a 'images' list containing all product images URLs.

        # images = ['http://image/1', 'http://image/2', ...]
        return render(request, 'edit_product.html',
            context = {
                'product': product,
                'categories': categories,
                'images': [image.url for image in pic_urls],
            }
        
        )
    elif request.method == 'POST':
        # Validate following fields that come in request.POST in the very same
        # way that you've done it in create_product view
        fields = ['name', 'sku', 'price']
        errors = {}
        
        # errors = {'name': 'This field is required.'}
        fields = ['name', 'sku', 'price']
        errors = {}
        
        for field in fields:
            if not request.POST[field]:
                errors[field] = 'This field is required.'
                
        # If no errors so far, validate each field one by one and use the same
        # errors dictionary created above in case that any validation fails
        if not errors:
            if len(request.POST['name'])>100:
                errors['name'] = "Name can't be more than 100 chars"
            if len(request.POST['description'])>1000:
                errors['description'] = "Description can't be more than 1000 chars"
            if float(request.POST['price']) > 10000.00 or float(request.POST['price'])<0:
                errors['price'] = "Price can't be greater than 10k"
            if len(request.POST['sku'])>8:
                errors['sku']= "SKU can't be more than 8 chars"


        #if any errors so far, render 'edit_product.html' sending errors and
        # categories as context

        if errors:
            return render(
                request,
                'edit_product.html',
                context={'errors': errors, 'categories': categories}
            )
        
        
        
        

        # If execution reaches this point, there aren't any errors.
        #Update product name, sku, price and description from the data that
        #come in request.POST dictionary.
        
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = float(request.POST['price'])
        product.sku = request.POST['sku']
   
    

        #Get proper category from the DB based on the category name given in
        # payload. Update product category.
        
        category = Category.objects.get(name=request.POST['category'])
        product.category = category
        product.save()

        # For updating the product images URLs, there are a couple of things that
        # you must consider:
        #1) Create a ProductImage object for each URL that came in payload and
        #    is not already created for this product.
        # 2) Delete all ProductImage objects for URLs that are created but didn't
        #    come in payload
        # 3) Keep all ProductImage objects that are created and also came in payload
        # <YOUR CODE HERE>
        current_images = product.productimage_set.all()
        current_image_urls = [pic.url for pic in current_images]
        new_pics = []
        for i in range(1,4):
            pic = request.POST.get('image-{}'.format(i))
            new_pics.append(pic)
            if pic not in current_image_urls:
                ProductImage.objects.create(
                    url = pic,
                    product = product
                    )
        for pic in current_images:
            if pic.url not in new_pics:
                pic.delete()
        product.save()    
        
        #Redirect to 'products' view
        return redirect('products')


def delete_product(request, product_id):
    #Get product with given product_id
    product = Product.objects.get(id=product_id)
    if request.method == 'GET':
        #render 'delete_product.html' sending product as context
        return render(
        request,
        'delete_product.html',
        context={'product': product}
        )
    elif request.method == "POST":
        # Delete product and redirect to 'products' view
        Product.objects.get(id=product_id).delete()
        return redirect('products')


def toggle_featured(request, product_id):
    # Get product with given product_id
    product = Product.objects.get(id=product_id)

    # Toggle product featured flag
    product.featured = not product.featured
    product.save()
    # Redirect to 'products' view
    return redirect('products')
