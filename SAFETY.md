# General lab rules

Last updated: 9 May 2023

**Table of Contents**

1. [Key hazards](#1-key-hazards)
2. [The basics](#2-the-basics)
3. [Soldering](#3-soldering)
4. [Quadcopter motors](#4-quadcopter-motors)
5. [LiPo batteries](#5-lipo-batteries)
6. [Test flights](#6-test-flights)
7. [Fire safety](#7-fire-safety)
8. [Emergency numbers](#8-emergency-numbers)
9. [Endnotes](#9-endnotes)



## 1. Key hazards

In the quadcopter lab (part of the autonomous systems lab) everyone should be aware of the following types of hazards:

- **Mechanical** (e.g., electric motors of quadcopters)
- **Thermal** (e.g., while soldering or glue guns)
- **Hazardous smokes** (e.g., from soldering)
- **Electrical** (low risk, as we typically work with low-voltage equipment)
- **Fire or explosions** e.g., from mishandling LiPo batteries

Our goal is to *identify* any possible hazards and *minimise* the likelihood of such hazards.

This document attempts to identify any possible risks and propose safety measures; it *complements* the [health and safety regulations and guidance](https://www.qub.ac.uk/directorates/EstatesDirectorate/UniversitySafetyService/HealthandSafetyPoliciesandGuidance/) of the university.


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


## 6. Test flights

> **Read first:** [Quadcopter motors](#4-quadcopter-motors)

When attaching the propellers, observe the following safety instructions:

- Attach the propellers carefully and tightly. 
- In case a propeller seems to vibrate excessively, disarm the motors, disconnect the battery, and (i) check the propellers for structural damage, (ii) make sure all screws are tightly screwed.
- Never use carbon fibre propellers as they can cause deep lacerations in case of an accident; use standard nylon propellers instead.

### 6.1. Before a test flight

1. Put on your protective glasses
2. Bring the quadcopter inside the netted area
3. After you power the quadcopter walk outside the net
4. If you need to use the test bench, make sure that (i) the ball joint is securely screwed on the base of the quadcopter, (ii) the base of the ball joint is not loose (check this before every flight)
5. Everyone must be alert.
6. Have the kill switch at the ready and be alert.
7. Make sure there are no gaps in the netting.


### 6.2. During a test flight

1. Do not enter the netting area.
2. Do not leave the drone unattended.
3. Be alert.
5. Do not go near the pinning propellers.
6. If any propeller or part of the drone comes loose, disarm immediately and disconnect the battery.

### 6.3. At the end of a test flight

1. Make sure you have disarmed using the kill switch on the RC.
2. Disconnect the battery.
3. Recharge the battery if necessary.



## 7. Fire safety

Firstly, familiarise with the [Fire Safety guidelines](https://www.qub.ac.uk/directorates/EstatesDirectorate/Services/FireSafety/) of the university.

In our lab a fire can be caused by any of the following reasons:

- Mishandling LiPo batteries
- Misusing the soldering iron or a glue gun
- Faulty electric circuits or misusing electric circuits (e.g., causing a short circuit)

To minimise the risk of fire we must always follow the [fire safety guidelines](https://www.qub.ac.uk/directorates/EstatesDirectorate/Services/FireSafety/) of the university. 

### 7.1. A few things about fire safety

- The main cause of fire is **people**
- The lab and the building is equipped with **fire doors** that can help to prevent the spread of smoke for at least 30 minutes to allow a safe exit in case of a fire. They are fitted with closing devices to ensure that the doors are in the correct position. Note that wedging fire doors open is illegal, against the university policy and unsafe. There are safe ways to hold them open if necessary.
- Do not use fire fighting equipment unless you have received training. Keep in mind that CO<sub>2</sub> fire extinguishers should be used on live electrical fires.
- Familiarise with the safety signage and notices in the building.


### 7.2. In case of a fire

If you discover a fire or even **suspect** a fire (through sight or smell), then **raise the alarm** by pressing the nearest available fire alarm manual call point.

The procedure is:

- Close the door
- Sound the fire alarm
- Ensure that Security have been informed
- Assist in the evacuation
- Tackle the fire if you are trained and someone is with you
- Immediately leave the building by the nearest available fire exit
- Do not use the elevators
- Do not stop to collect your personal belongings
- Report to the designated fire assembly point
- Do not re-enter the building until you are told it is safe to do so


### 8. Emergency numbers

- QUB security on extension 2222
- Off campus: dial 999 and ask for the fire and rescue service





## 9. Endnotes

- No equipment leaves the lab
- Before you leave the lab:
  - switch off any electronics/electrical equipment (esp. battery chargers and soldering irons)
  - turn off the lights
  - lock the door

 