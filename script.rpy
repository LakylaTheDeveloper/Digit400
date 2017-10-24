

label start:

    scene bg room
    with fade

    show sylvie2_giggle
    with dissolve
    
    "Digit Classmate" "Good Morning"

    "Me" "Good Morning"
    
    "Digit Classmate" "Class was very interesting today! Right?"

    "I can't bring myself to admit that it all went in one ear and out the other."

    "Me" "Yeah.... "

    show sylvie2_normal 
    with dissolve

    "Digit Classsmate" "Did you start that project?"
    
menu:
    "That \"hello world\" project? yeah i did.":
            jump good
    "What project??":
            jump bad
        
label good:
    "Digit Classmate" "Great i did too!"
    jump end

label bad:
    "Digit Classmate" "That \"hello world\" project it's due Tonight. Better get started."
    jump end
    
label end:
    "Digit classmate" "later."

   
".:. Good Ending."
return