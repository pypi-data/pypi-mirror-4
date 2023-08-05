(function($) {
    
    Number.prototype.currency = function(monetary){
        if (this && this > 0){
            return monetary +' '+ this.toFixed(2).replace('.', ',');
        }

        return monetary +' 0';
    };

    $.fn.shippingFreight = function(customOptions) {  //Add the function
        var options = $.extend({}, $.fn.shippingFreight.defaultOptions, customOptions);
        return this.each(function() { //Loop over each element in the set and return them to keep the chain alive.
            var $this = $(this);
            
            $countries = $this.find("select[name='country_code']");
            $fulladdress = $this.find(".shipping-full-address");
            $states = $fulladdress.find(".shipping-states");
            $shippingCost = $this.find('.shipping-freight-cost');

            $countries.unbind().on('change', function(e){
                country_code = $countries.val();
                $country = $countries.find("option[value='"+country_code+"']");

                $shippingCost.html('');
                if ($country.attr('fulladdress') == 'True'){
                    $fulladdress.show();

                    $states.children('span').html('carregando...');
                    $.ajax({
                        url: options.urls.states.replace('{country}', $countries.val()),
                        type: 'GET',
                        success: function(response){

                            $states.children('span').html();
                            if (response.states.length === 0){
                                $states.children('span').html('<input type="text" name="state" />');
                            }
                            else{
                                $select = $('<select name="state"></select>');
                                $.each(response.states, function(){
                                    $select.append('<option value="'+ this.id +'">'+ this.name +'</option>');
                                });

                                $states.children('span').html($select);
                            }
                            
                        }
                    });
                }
                else{
                    $fulladdress.hide();
                }
                
            });
            $countries.trigger('change');

            $this.find('.calculate').unbind().on('click', function(e){
                e.preventDefault();

                $this.addClass('shipping-loaindg');
                $shippingCost.html('');

                $.ajax({
                    type: 'POST',
                    url: options.urls.estimation,
                    data: $this.children('form').serialize(),
                    success: function(response){
                        $this.removeClass('shipping-loaindg');

                        if (response.error){
                            $shippingCost.html(response.error);
                        }
                        else{
                            $shippingCost.html(parseFloat(response.price).currency(options.monetary));
                        }
                    }
                });
            });
        });
    };
 
    $.fn.shippingFreight.defaultOptions = {
        monetary : "R$",
        urls: {
            states: '/shipping/countries/{country}.json',
            estimation: '/shipping/estimation/'
        }
    };
})(jQuery);