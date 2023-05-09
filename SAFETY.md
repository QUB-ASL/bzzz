# General lab rules

Last updated: 7 May 2023

## 1. Key hazards

In the quadcopter lab (part of the autonomous systems lab) everyone should be aware of the following types of hazards:

- **Mechanical** (e.g., electric motors of quadcopters)
- **Thermal** (e.g., while soldering or glue guns)
- **Hazardous smokes** (e.g., from soldering)
- **Electrical** (low risk, as we typically work with low-voltage equipment)
- **Fire or explosions** e.g., from mishandling LiPo batteries

Our goal is to *identify* any possible hazards and *minimise* the likelihood of such hazards.

This document attempts to identify any possible risks and propose safety measures; it *complements* the [health and safety regulations and guidance](https://www.qub.ac.uk/directorates/EstatesDirectorate/UniversitySafetyService/HealthandSafetyPoliciesandGuidance/) of the university.

**Table of Contents**

1. [Soldering](#soldering)
2. [Rotating equipment](#rotating-equipment)
3. [LiPo batteries](#lipo-batteries)
4. [Testing quadcopters](#testing-quadcopters)
5. [Fire safety](#fire-safety)


## 2. The basics

- Health and safety is everyone's responsibility
- If you suspect that you have identified a hazard, you should contact your line manager
- Any accidents must be reported to your line manager

> Important: In the case of an **emergency** where there is an imminent and serious danger to people or property, then the appropriate emergency services should be called. To do this from a University telephone, dial **2222** to contact the University Control Room operator or 9-999 to contact Police, Fire, and Ambulance services.


## 3. Soldering 

Some common risks associated with soldering include exposure to hazardous chemicals, eye injuries, burns, and inhalation of fumes and smoke. When soldering, the solder and flux emit fumes that can cause respiratory issues if inhaled in high quantities. Additionally, the soldering iron can become extremely hot (around 400C) and cause burns to the skin or eyes if safety controls are not in place. 

As a result:

- Do not attempt to use the soldering iron unless you have been trained; contact your line manager first.
- Never touch the element of the soldering iron.
- Use tweezers where possible and avoid touching the wires you are soldering with your hands.
- Keep the cleaning sponge wet during use.
- Always return the soldering iron to its stand when not in use. Never put it down on the workbench.
- Turn unit off and unplug when not in use.
- Wear eye protection as the solder can "spit" in any direction.
- Use rosin-free and lead-free solders wherever possible.
- Always wash your hands with soap and water after soldering.

You may find more information at the [webpage](https://safety.eng.cam.ac.uk/safe-working/copy_of_soldering-safety) of the Dept of Engineering Health and Safety of the University of Cambridge.


### 4. Quadcopter motors

The brushless motors used on a quadcopter can spin up to several thousands RPM, therefore, if you are close to a spinning motor you risk getting injured. 

At all times, observe the following safety instructions:

- Never touch a spinning motor with your hands or with a tool or through a piece of clothing
- When you are close to a spinning motor you must not wear a lanyard, tie, scarfs. If you are wearing a hoodie with drawstrings, put them inside so that they do not hang. Any hanging string is likely to be caught up by a motor leading to injury.
- Wear protective gloves: even when you are operating a motor without the propellers attached, there is a chance that a bolt becomes loose and flies off at a high speed.
- Periodically (at least twice a day), make sure that the little grub screws at the bottom part of the motors are not loose. Of course, you should not tighten them too much.
- At least once a day and every time before performing test flights, you should check to make sure that the bolts that hold the motors on the horizontal metallic rods are tightly screwed.

> Keep in mind: when the ESCs are **armed**, the motors can start to rotate at any time.



## 5. LiPo batteries

### 5.1. Hazards 

There are several hazards associated with LiPo batteries, such as:

- **Fire and explosion**: Mishandling of LiPo batteries can lead to fire, explosions, and toxic smoke inhalation. This is because LiPo batteries contain highly volatile and flammable electrolytes that can catch fire if they are damaged, overcharged, or punctured.
- **Thermal runaway**: LiPo batteries can undergo a process called thermal runaway, where a small thermal event or overcharging can cause the battery to rapidly heat up, leading to a chain reaction and causing the battery to vent, catch fire, or explode.
- **Physical damage**: LiPo batteries are sensitive to physical damage, such as punctures or crushing, which can cause them to catch fire or explode.
- **Voltage deviation**: If the voltages across the cells deviate too much from each other (5mV ~ 10Mv), the battery can become unstable and dangerous.

Therefore, it is important to handle LiPo batteries with care.

<img src="https://m.media-amazon.com/images/I/71o7wIMQmDL.jpg" width=200>


### 5.2. How to charge and store a LiPo battery

- LiPo batteries should not be stored fully charged. Instead, they should be brought down to **storage charge**, which corresponds to about 3.8V per cell. A LiPo battery not at storage voltage will degrade and the effect is cumulative: keeping a battery fully charged for 10 consecutive days is the same as keeping it fully charged for 1 day on 10 different days. 

> It is highly recommended that we storage-charge the LiPo batteries at the end of every day.

- It is recommended to use a **LiPo battery bag** when charging a LiPo battery to provide an extra layer of protection against fire and explosion.
- Never let a battery voltage fall below critical level. If the voltage in a cell falls below 3.2V it can be permanently damaged. 
- Never overcharge a battery. If the voltage of a cell exceeds 4.2V it can burst into flames. 
- Never short-circuit a battery.
- Follow proper disposing guidelines before discarding a battery.
- Any bulge, smoke from a battery must be dealt with serious caution.

> Read more about LiPo batteries [here](https://fpvfc.org/beginners-guide-to-lipo-batteries).


## Test flights

When attaching the propellers, observe the following safety instructions:

- Attach the propellers carefully and tightly. 
- In case a propeller seems to vibrate excessively, disarm the motors
- Never use carbon fibre propellers as they can cause deep lacerations in case of an accident; use standard nylon propellers instead.

- Before beginning to operate/test the drone:
    1. Wear safety glasses and proper safety gear.
    2. Drone must always stay inside the netting.
    3. Make sure everyone is outside the netting.
    4. Fasten the drone properly to the safety harness.
    5. Fasten the propellers properly.
    6. Make sure every electric connection, nut and bolt, screw are snug and tight.
    7. Everyone must be alert.
    8. Never fly the drone alone, have an expert to supervise.
    9. Have the kill switch at the ready and be alert.
    10. Make sure there are no gaps in the netting.
    11. Follow these instructions while testing the drone as well.
3. While testing the drone:
    1. Do not enter the netting area.
    2. Do not leave the drone unattended.
    3. Be alert and agile.
    4. If it is necessary to go near the drone, make sure to have no loose clothing is hanging from you.
    5. Never try to touch the propellers.
    6. If any propeller, part of the drone comes loose, kill the drone immediately.
    7. If the drone comes loose, kill the drone immediately and disconnect the battery.
4. After finishing the drone test/ operation:
    1. Disconnect the battery.
    2. Tighten all the parts once more.
    3. Recharge the battery if necessary.








## Fire safety

Firstly, familiarise with the [Fire Safety guidelines](https://www.qub.ac.uk/directorates/EstatesDirectorate/Services/FireSafety/) of the university.



## 5. Endnotes

- No equipment leaves the lab
- Before you leave the lab:
  - switch off any electronics/electrical equipment (esp. battery chargers and soldering irons)
  - turn off the lights
  - lock the door

 