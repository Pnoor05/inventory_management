/**
 * Client-side form validation
 * Preserves all original validation logic
 */
export class FormValidator {
    static init() {
        this.setupProductFormValidation();
        this.setupLoginFormValidation();
    }

    static setupProductFormValidation() {
        const forms = document.querySelectorAll('#productForm, #editForm');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateProductForm(form)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);

            // Real-time validation
            form.querySelectorAll('input').forEach(input => {
                input.addEventListener('input', () => {
                    if (input.name === 'unit_price') {
                        this.validatePrice(input);
                    }
                });
            });
        });
    }

    static validateProductForm(form) {
        let isValid = true;
        
        // Validate price
        const priceInput = form.querySelector('input[name="unit_price"]');
        if (priceInput && !this.validatePrice(priceInput)) {
            isValid = false;
        }

        // Validate quantity
        const qtyInput = form.querySelector('input[name="quantity_in_stock"]');
        if (qtyInput && !this.validateQuantity(qtyInput)) {
            isValid = false;
        }

        return isValid;
    }

    static validatePrice(input) {
        const value = parseFloat(input.value);
        if (isNaN(value) || value <= 0) {
            input.setCustomValidity('Price must be a positive number');
            return false;
        }
        input.setCustomValidity('');
        return true;
    }

    static validateQuantity(input) {
        const value = parseInt(input.value);
        if (isNaN(value) || value < 0) {
            input.setCustomValidity('Quantity must be 0 or greater');
            return false;
        }
        input.setCustomValidity('');
        return true;
    }

    static setupLoginFormValidation() {
        const form = document.getElementById('loginForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        }
    }
}