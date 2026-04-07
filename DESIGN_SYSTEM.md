# HR Management System - Design System Documentation

## Quick Start

The HR Management System has a reusable design system that you can copy and use across all pages.

### View the Design System
Go to: **http://127.0.0.1:8000/design/**

This page shows live examples of all available design components.

---

## Files Included

1. **design_template.html** - Visual showcase of all components
2. **design-system.css** - Standalone CSS file with all styles
3. **This documentation** - How to use everything

---

## Color Palette

All colors are defined as CSS variables for easy customization:

```css
--primary-color: #1e40af           /* Dark Blue */
--secondary-color: #3b82f6         /* Light Blue */
--light-blue: #e0e7ff              /* Very Light Blue */
--light-gray: #f3f4f6              /* Light Gray */
--dark-text: #1f2937               /* Dark Gray Text */
--gray-text: #6b7280               /* Medium Gray Text */
--border-color: #e5e7eb            /* Light Border */
--success-color: #10b981           /* Green */
--error-color: #ef4444             /* Red */
--warning-color: #f59e0b           /* Amber */
```

---

## Layout Components

### Container
```html
<div class="design-container">
    <!-- Content centered on light blue gradient background -->
</div>
```

### Card
```html
<div class="design-card">
    <!-- White card with shadow -->
</div>
```

### Two Column Layout
```html
<div class="design-card design-two-column">
    <div class="design-column-left">
        <!-- Left side with gradient background -->
    </div>
    <div class="design-column-right">
        <!-- Right side with white background -->
    </div>
</div>
```

**Responsive:** Automatically stacks to single column on mobile (< 768px)

---

## Typography

### Title
```html
<h2 class="design-title">Your Title</h2>
```
- Size: 28px
- Weight: 700 (bold)
- Color: Primary Blue
- Letter spacing: -0.5px

### Subtitle
```html
<p class="design-subtitle">Your subtitle text</p>
```
- Size: 16px
- Color: Medium Gray
- Line height: 1.6

### Label
```html
<label class="design-label">Field Label</label>
```
- Size: 13px
- Weight: 600
- Color: Dark Text
- All caps with letter spacing

---

## Form Elements

### Text Input
```html
<div class="design-form-group">
    <label class="design-label">Username</label>
    <input type="text" class="design-input" placeholder="Enter username">
</div>
```

### Password Input
```html
<div class="design-form-group">
    <label class="design-label">Password</label>
    <input type="password" class="design-input" placeholder="Enter password">
</div>
```

### Email Input
```html
<div class="design-form-group">
    <label class="design-label">Email</label>
    <input type="email" class="design-input" placeholder="Enter email">
</div>
```

### Number Input
```html
<div class="design-form-group">
    <label class="design-label">Age</label>
    <input type="number" class="design-input" placeholder="Enter age">
</div>
```

### Date Input
```html
<div class="design-form-group">
    <label class="design-label">Date</label>
    <input type="date" class="design-input">
</div>
```

### Textarea
```html
<div class="design-form-group">
    <label class="design-label">Message</label>
    <textarea class="design-textarea" placeholder="Your message..."></textarea>
</div>
```

### Select Dropdown
```html
<div class="design-form-group">
    <label class="design-label">Option</label>
    <select class="design-select">
        <option>Choose option</option>
        <option>Option 1</option>
        <option>Option 2</option>
    </select>
</div>
```

### Checkbox
```html
<label class="design-checkbox">
    <input type="checkbox"> Remember me
</label>
```

### Radio Button
```html
<label class="design-radio">
    <input type="radio" name="option"> Option 1
</label>
```

---

## Buttons

### Primary Button (Main Action)
```html
<button class="design-btn design-btn-primary">Sign In</button>
```
- Full width with gradient background
- Blue color
- Hover effect: raises up slightly

### Secondary Button (Alternative Action)
```html
<button class="design-btn design-btn-secondary">Cancel</button>
```
- Light gray background
- Full width
- Hover effect: darker gray

### Danger Button (Delete/Destructive)
```html
<button class="design-btn design-btn-danger">Delete</button>
```
- Red background
- For destructive actions

### Success Button
```html
<button class="design-btn design-btn-success">Save</button>
```
- Green background
- For completed/confirmed actions

### Warning Button
```html
<button class="design-btn design-btn-warning">Warnings</button>
```
- Amber background
- For warning/caution actions

### Link Button (Text Link Style)
```html
<a href="#" class="design-btn design-btn-link">Forgot Password?</a>
```
- No background
- Blue text
- Text decoration on hover

---

## Alerts

### Success Alert
```html
<div class="design-alert design-alert-success">
    ✓ Success! Your changes have been saved.
</div>
```
- Green border and background
- Used for successful operations

### Error Alert
```html
<div class="design-alert design-alert-error">
    ✗ Error! Something went wrong.
</div>
```
- Red border and background
- Used for errors and failures

### Info Alert
```html
<div class="design-alert design-alert-info">
    ℹ Info! This is an informational message.
</div>
```
- Blue border and background
- Used for informational messages

### Warning Alert
```html
<div class="design-alert design-alert-warning">
    ⚠ Warning! Please be careful.
</div>
```
- Amber border and background
- Used for warnings

---

## Helper Classes

### Flexbox
```html
<div class="design-flex">
    <label class="design-checkbox">
        <input type="checkbox"> Remember me
    </label>
    <a href="#" class="design-btn-link">Forgot Password?</a>
</div>
```
- Distributes items horizontally with space between
- Responsive: stacks on mobile

### Flex Column
```html
<div class="design-flex-column">
    <!-- Items stack vertically -->
</div>
```

### Divider
```html
<div class="design-divider"></div>
```
- Horizontal line separator

### Text Alignment
```html
<p class="design-text-center">Centered text</p>
<p class="design-text-right">Right aligned</p>
```

### Text Styling
```html
<p class="design-text-muted">Gray muted text</p>
<p class="design-text-error">Red error text</p>
```

### Spacing Classes
```html
<!-- Margin Top -->
<div class="design-mt-10">10px margin top</div>
<div class="design-mt-20">20px margin top</div>
<div class="design-mt-30">30px margin top</div>

<!-- Margin Bottom -->
<div class="design-mb-10">10px margin bottom</div>
<div class="design-mb-20">20px margin bottom</div>
<div class="design-mb-30">30px margin bottom</div>

<!-- Padding -->
<div class="design-p-10">10px padding</div>
<div class="design-p-20">20px padding</div>
<div class="design-p-30">30px padding</div>
```

---

## Complete Login Form Example

```html
{% extends "base.html" %}

{% block content %}
<div class="design-container">
    <div class="design-card design-two-column">
        <!-- Left Side -->
        <div class="design-column-left">
            <div class="design-icon">🏢</div>
            <h2 class="design-title">HR Management</h2>
            <p class="design-subtitle">Connect with your team and manage your workspace</p>
        </div>

        <!-- Right Side -->
        <div class="design-column-right">
            <form method="POST">
                {% csrf_token %}
                
                <div class="design-form-group">
                    <label class="design-label">Username</label>
                    <input type="text" class="design-input" placeholder="Enter your username" required>
                </div>

                <div class="design-form-group">
                    <label class="design-label">Password</label>
                    <input type="password" class="design-input" placeholder="Enter your password" required>
                </div>

                <div class="design-flex">
                    <label class="design-checkbox">
                        <input type="checkbox"> Remember me
                    </label>
                    <a href="{% url 'forgot_password' %}" class="design-btn-link">Forgot Password?</a>
                </div>

                <button type="submit" class="design-btn design-btn-primary">Sign In</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

---

## Complete Form Page Example

```html
{% extends "base.html" %}

{% block content %}
<div class="design-container">
    <div class="design-card design-p-30" style="max-width: 600px; width: 100%;">
        <h2 class="design-title">Add New Employee</h2>
        
        {% if error_message %}
        <div class="design-alert design-alert-error">{{ error_message }}</div>
        {% endif %}
        
        <form method="POST">
            {% csrf_token %}
            
            <div class="design-form-group">
                <label class="design-label">First Name</label>
                <input type="text" class="design-input" name="first_name" required>
            </div>

            <div class="design-form-group">
                <label class="design-label">Last Name</label>
                <input type="text" class="design-input" name="last_name" required>
            </div>

            <div class="design-form-group">
                <label class="design-label">Email</label>
                <input type="email" class="design-input" name="email" required>
            </div>

            <div class="design-form-group">
                <label class="design-label">Department</label>
                <select class="design-select" name="department" required>
                    <option>Select Department</option>
                    <option>HR</option>
                    <option>IT</option>
                    <option>Sales</option>
                </select>
            </div>

            <div class="design-form-group">
                <label class="design-label">Notes</label>
                <textarea class="design-textarea" name="notes" placeholder="Any additional notes..."></textarea>
            </div>

            <div class="design-flex">
                <button type="submit" class="design-btn design-btn-primary">Save Employee</button>
                <a href="{% url 'employee_list' %}" class="design-btn design-btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
```

---

## How to Use in Your Pages

### Option 1: Copy CSS Classes
1. Copy the CSS from `static/css/design-system.css`
2. Paste into your own stylesheet or `<style>` block
3. Use the class names in your HTML

### Option 2: Link the CSS File
Add to your template's `<head>`:
```html
<link rel="stylesheet" href="{% static 'css/design-system.css' %}">
```

### Option 3: Copy from Design Template
1. Go to http://127.0.0.1:8000/design/
2. Right-click → "View Page Source"
3. Copy the HTML and CSS you need
4. Paste into your template

---

## Customization

### Change Primary Color
In `design-system.css`, change:
```css
--primary-color: #1e40af;  /* Change this hex value */
```

### Adjust Spacing
Modify padding/margin in specific components:
```css
.design-input {
    padding: 12px 14px;  /* Change these values */
}
```

### Change Button Size
Modify button padding:
```css
.design-btn {
    padding: 12px 20px;  /* Change first value for height, second for width */
}
```

---

## Responsive Behavior

All components are responsive:
- **Desktop (>768px):** Full size, two-column layouts work
- **Tablet (480px - 768px):** Slightly reduced padding, stacked columns
- **Mobile (<480px):** Compact layout, full-width buttons and inputs

---

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

---

## Questions?

For more information or to view live examples:
- Visit: http://127.0.0.1:8000/design/
- Check the design_template.html file for code examples

Enjoy! 🎨
